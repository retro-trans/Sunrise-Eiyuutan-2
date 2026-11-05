import json,struct,unittest
from test_binary import ROOT,Cpu
from elf import PATH,Elf
from message_pages import pages
from textcodec import encode,controls
from story_layout import wrap_row,wrap_body,measure,WIDTH,FINAL_WIDTH


class StoryLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Derive the actual shipped font metrics without requiring an old,
        # disposable preview build's report to still be on disk.
        import fontgen
        cls.widths=[13]*128;cls.widths[32]=5
        for code,(_,width) in fontgen.build_ascii(26).items():cls.widths[code]=width

    def test_complete_meaning_survives_reflow_with_exact_native_cues(self):
        text='\n{C:81930100}{C:81958296881D00000000}'+('This complete sentence retains every word. '*7).strip()+'\n\n{x00}'
        wrapped,report=wrap_row(text,self.widths,False)
        self.assertEqual(controls(text),controls(wrapped));self.assertEqual(text.split(),wrapped.split())
        self.assertEqual(len(pages(encode(text))),len(pages(encode(wrapped))))
        self.assertGreater(report[0]['lines'],3)
        with self.assertRaises(ValueError):wrap_row(text,self.widths)

    def test_player_name_reserves_maximum_eight_fullwidth_glyphs(self):
        self.assertEqual(measure('{C:819782960000}',self.widths),224)
        text='{C:819782830400}{C:819782960000} Akatsuki{C:819782830000}'
        self.assertLessEqual(measure(text,self.widths),504)
        self.assertEqual(controls(text),controls(wrap_body(text,self.widths)))

    def test_color_and_function_only_boundaries_stay_in_order(self):
        text='\n{C:819582860100010056000000}\n{C:81930700}{C:819582963F1E00000000}A complete sentence.\n\n{C:819582860100010000000000}\n\n{x00}'
        wrapped,report=wrap_row(text,self.widths)
        self.assertEqual(encode(text),encode(wrapped));self.assertEqual(len(report),1)

    def test_centered_heading_uses_proportional_space_width(self):
        text='\n{C:81930000}{C:819782830300}Moving Your Battleship\n\n{x00}'
        result,report=wrap_row(text,self.widths,centered_calls=(1,))
        body=pages(encode(result))[1]['body'].decode('ascii').rstrip('\n');padding=len(body)-len(body.lstrip())
        width=measure('Moving Your Battleship',self.widths);left=padding*(self.widths[32]+2)
        self.assertLess(abs(left-(504-left-width)),2*(self.widths[32]+2))
        self.assertEqual(controls(text),controls(result));self.assertTrue(report[0]['centered'])

    def test_unprofiled_story_commands_and_unbreakable_words_fail(self):
        for text in ('{C:2335}Title','{C:819782830500}Title','W'*100):
            with self.assertRaises(ValueError):wrap_body(text,self.widths)

    def test_battle_color_six_is_zero_width_without_admitting_other_modes(self):
        text='{C:819782830600}Return{C:819782830000}'
        self.assertEqual(measure(text,self.widths,'battle-tutorial'),measure('Return',self.widths))
        with self.assertRaises(ValueError):measure(text,self.widths)
        for bad in ('{C:819782830500}Return','{C:2335}Return'):
            with self.assertRaises(ValueError):wrap_body(bad,self.widths,'battle-tutorial')

    def test_prompt_reflow_preserves_complete_words_and_unchanged_short_pages(self):
        text="Sorry, Lun. I have to go. Wait here for me."
        self.assertEqual(measure(text,self.widths),491)
        result=wrap_body(text,self.widths)
        self.assertEqual(result.split(),text.split())
        self.assertEqual(len(result.split('\n')),2)
        self.assertLessEqual(measure(result.split('\n')[-1],self.widths),FINAL_WIDTH)
        self.assertTrue(all(measure(x,self.widths)<=WIDTH for x in result.split('\n')))
        self.assertEqual(wrap_body('A short complete sentence.',self.widths),'A short complete sentence.')
        # A single token cannot be broken or silently squeezed to make room.
        with self.assertRaises(ValueError):wrap_body('A'*40,[10]*128)

    def test_original_prompt_machine_code_uses_cursor_plus_twenty_six(self):
        elf=Elf(PATH.read_bytes())
        for cursor in (FINAL_WIDTH,499):
            cpu=Cpu();cpu.put(0x12d268,elf.at(0x12d268,68))
            window,text,prompt=0x700000,0x700100,0x700200
            cpu.put(0x239580,struct.pack('<I',window));cpu.put(0x239594,struct.pack('<I',prompt))
            cpu.put(window,struct.pack('<I',text));cpu.put(window+0x14,struct.pack('<II',cursor,56))
            cpu.put(window+0x38,struct.pack('<II',6,26));cpu.put(text+0x18,struct.pack('<II',118,342))
            cpu.reg('gp',0x23f570);cpu.reg('ra',0xffff0000);cpu.reg('a0',1)
            cpu.run(0x12d268)
            x,y,w,h=struct.unpack('<4I',cpu.get(prompt+0x18,16))
            self.assertEqual((x,y,w,h),(118+cursor,398,6,26))
            self.assertEqual(cpu.get(0x239598,4),struct.pack('<I',1))
            # Execute the original triangle vertex overrides, after the native
            # frame routine has supplied its upper-left and lower-right points.
            sp=0x1800000;cpu.reg('sp',sp)
            cpu.put(sp+0x40,struct.pack('<I',x));cpu.put(sp+0x64,struct.pack('<I',y+h))
            cpu.put(0x110a8c,elf.at(0x110a8c,0x58))
            cpu.run(0x110a8c,stop=0x110ae4)
            left,top=struct.unpack('<II',cpu.get(sp+0x40,8))
            right=struct.unpack('<I',cpu.get(sp+0x50,4))[0]
            tip,bottom=struct.unpack('<II',cpu.get(sp+0x60,8))
            self.assertEqual((left,right,tip,top,bottom),(x+8,x+26,x+17,y+8,y+24))
            self.assertEqual(right<=118+WIDTH,cursor==FINAL_WIDTH)

    def test_read_only_prompt_inspection_keeps_native_width_and_rejects_bad_pointer(self):
        import sys
        sys.path.insert(0,str(ROOT/'tools/dbg'))
        from message_state import prompt_state
        ee=bytearray(0x240000);obj=0x210000
        struct.pack_into('<I',ee,0x239594,obj);struct.pack_into('<I',ee,0x239598,1)
        struct.pack_into('<4I',ee,obj+0x18,617,398,6,26)
        original=bytes(ee);result=prompt_state(ee)
        self.assertEqual(result['last_glyph_size'],[6,26])
        self.assertEqual(result['triangle_right'],643)
        self.assertEqual(bytes(ee),original)
        struct.pack_into('<I',ee,0x239594,len(ee)-4)
        with self.assertRaises(ValueError):prompt_state(ee)


if __name__=='__main__':unittest.main()
