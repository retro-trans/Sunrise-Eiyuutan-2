"""Capture routing must preserve old paths and reject missing/escaping destinations."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'dbg'))
import control

class CaptureStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.ui=self.root/'work/ui';self.ui.mkdir(parents=True)
        self.swap=patch.object(control,'ROOT',self.root);self.swap.start();self.addCleanup(self.swap.stop)
    def config(self,value):
        (self.ui/'capture-storage.json').write_text(json.dumps(value),encoding='utf-8')
    def test_absent_config_preserves_legacy_directory(self):
        self.assertEqual(control.capture_directory(),self.ui/'shots')
    def test_config_routes_to_existing_project_child(self):
        dest=self.ui/'shots/spillover-122';dest.mkdir(parents=True)
        self.config(dict(shots_subdirectory='spillover-122'))
        self.assertEqual(control.capture_directory(),dest)
        marker=self.ui/'shots/old-evidence';marker.write_bytes(b'preserve')
        self.assertEqual(marker.read_bytes(),b'preserve')
    def test_missing_configured_directory_fails_before_state_save(self):
        self.config(dict(shots_subdirectory='missing'))
        with self.assertRaises(FileNotFoundError):control.capture_directory()
    def test_bad_configs_cannot_escape_project_shots(self):
        for value in ({'shots_subdirectory':'../outside'}, {'shots_subdirectory':'K:/elsewhere'},
                      {'shots_subdirectory':''}, {'shots_subdirectory':None},
                      {'shots_subdirectory':'ok','extra':True}, []):
            with self.subTest(value=value):
                self.config(value)
                with self.assertRaises(ValueError):control.capture_directory()

if __name__=='__main__':unittest.main()
