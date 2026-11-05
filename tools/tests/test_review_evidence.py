import hashlib,unittest
from test_binary import ROOT
from strip_jp import attach_fit_evidence

class EvidenceTests(unittest.TestCase):
    def test_wording_change_expires_versioned_display_approval(self):
        row=dict(en='Complete wording',rendered_evidence=dict(build='0.1.13',draft_sha256=hashlib.sha256(b'Complete wording').hexdigest(),built_row_sha256='a'*64,native_sha256='b'*64,pages=2,audit='work/ui/audits/example/audit.json',build_elf_sha256='c'*64))
        clean=dict(review=dict(rendered_fit='passed'));attach_fit_evidence(clean,row)
        self.assertEqual(clean['rendered_evidence']['build'],'0.1.13')
        row['en']='Changed wording';changed=dict(review=dict(rendered_fit='passed'));attach_fit_evidence(changed,row)
        self.assertEqual(changed['review']['rendered_fit'],'pending');self.assertNotIn('rendered_evidence',changed)
        with self.assertRaises(ValueError):attach_fit_evidence(dict(review=dict(rendered_fit='passed')),dict(en='No evidence'))

if __name__=='__main__':unittest.main()
