"""Inventory compiled translation proposals by source ID, without building or testing patches."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from elf import ROOT


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def language_ready(row):
    review = row.get('review', {})
    return review.get('accuracy') == 'independent-reviewed' and all(
        isinstance(review.get(stage), str) and review[stage] and 'pending' not in review[stage].lower()
        for stage in ('editorial', 'name_audit', 'proofread'))


def collect():
    catalogs = {}
    sources = {}
    for path in sorted((ROOT / 'work/source/candidates').rglob('*.json')):
        document = read(path)
        if not isinstance(document, dict) or not isinstance(document.get('rows'), list):
            continue
        for row in document['rows']:
            if not isinstance(row, dict) or not all(key in row for key in ('id', 'raw', 'jp')):
                continue
            if row['id'] in sources:
                raise ValueError('Duplicate catalog source ID: ' + row['id'])
            sources[row['id']] = row
        catalogs[str(path.relative_to(ROOT)).replace('\\', '/')] = digest(path.read_bytes())
    offers = {}
    artifacts = {}
    suffixes = {}
    for path in sorted((ROOT / 'work/translation/en/pending').glob('compiled*.json')):
        document = read(path)
        if not isinstance(document, dict) or not isinstance(document.get('rows'), list):
            continue
        relative = str(path.relative_to(ROOT)).replace('\\', '/')
        artifacts[relative] = digest(path.read_bytes())
        mechanical = document.get('stage') == 'Mechanical glossary-match queue537'
        for row in document['rows']:
            source = sources.get(row['id'])
            if source is None:
                raise ValueError('Proposal has no catalog source: ' + row['id'])
            if row['source_sha256'] != digest(bytes.fromhex(source['raw'])):
                raise ValueError('Proposal source hash differs: ' + row['id'])
            if row.get('source_jp') != source['jp']:
                raise ValueError('Proposal source text differs: ' + row['id'])
            if isinstance(row.get('en'), str):
                if row.get('en_utf8_sha256') and row['en_utf8_sha256'] != digest(row['en'].encode('utf-8')):
                    raise ValueError('Proposal English hash differs: ' + row['id'])
                rank = 3 if language_ready(row) else 1 if mechanical else 2
                offers.setdefault(row['id'], []).append((rank, row, relative))
            sub = row.get('literal_subspan_proposal')
            if sub and isinstance(sub.get('en'), str):
                key = (row['id'], sub['va'])
                suffixes.setdefault(key, []).append((3 if language_ready(sub) else 2, sub, relative))

    def select(identifier, candidates):
        rank = max(item[0] for item in candidates)
        best = [item for item in candidates if item[0] == rank]
        wording = {item[1]['en'] for item in best}
        if len(wording) != 1:
            return dict(id=identifier, status='conflicting-proposals', proposals=[dict(en=q['en'], artifact=p) for _, q, p in best])
        row = best[0][1]
        return dict(id=identifier, status={1: 'mechanical-unreviewed', 2: 'draft-review-pending', 3: 'language-ready'}[rank],
                    en=row['en'], en_utf8_sha256=digest(row['en'].encode('utf-8')),
                    source_sha256=row['source_sha256'], artifacts=[item[2] for item in best],
                    native_integration='pending', rendered_fit='pending')

    rows = [select(identifier, offers[identifier]) for identifier in sorted(offers)]
    suffix_rows = []
    for (identifier, va), candidates in sorted(suffixes.items()):
        row = select(identifier + '#subspan-' + format(va, '08X'), candidates)
        row.update(parent_source_id=identifier, va=va, replacement_scope='Isolated literal suffix only; never replace the whole mixed object.')
        suffix_rows.append(row)
    counts = Counter(row['status'] for row in rows)
    summary = dict(catalog_candidates=len(sources), whole_proposal_source_ids=len(rows), whole_proposals_by_status=dict(counts),
                   distinct_language_ready_English=len({row['en'] for row in rows if row['status'] == 'language-ready'}),
                   isolated_suffix_proposals=len(suffix_rows), isolated_suffixes_by_status=dict(Counter(row['status'] for row in suffix_rows)),
                   candidates_without_whole_English_proposal=len(sources.keys() - offers.keys()),
                   scope='Compiled scanner candidates only. Raw counts include artifacts, internal keys and possible unused text. Structured ATMB coverage is separate.',
                   testing='None. This is proposal inventory and source provenance, not native admission, font/layout or in-game validation.',
                   whole_game_complete=False)
    return summary, dict(language='en', scope=summary['scope'], use_for_native_patch=False,
                         notice='Contains reviewed, draft and unreviewed proposals. Individual status is authoritative; technical integration is pending.', rows=rows, isolated_suffixes=suffix_rows,
                         guarded_catalogs=catalogs, guarded_proposal_artifacts=artifacts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    summary, export = collect()
    print(json.dumps(summary, indent=1))
    print('Sample saved proposals:')
    for row in export['rows'][:4] + export['rows'][-4:]:
        print(json.dumps(row, ensure_ascii=False))
    if args.write:
        for path, data in [(ROOT / 'docs/compiled_coverage.json', summary),
                           (ROOT / 'work/translation/en/compiled-proposals.en.json', export)]:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('WRITE: compiled proposal inventory and English-only export. No build or tests.')
    else:
        print('DRY: --write saves inventory and English-only proposals; no patch output.')


if __name__ == '__main__':
    main()
