#!/usr/bin/env python3
"""Build docs/data/sightings.json from the archived NUFORC index and curated news events.

Never invents sightings. Dates, places and quotes stay inside what the sources say.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "data" / "sightings.json"

SKIP_NUFORC = {
    "46184",   # creature report, not a sky object
    "152885",  # witness says they did not see a UFO
}

# Treat later report as an addendum to the earlier one
MERGE_INTO = {
    "93383": "93382",
    "178262": "178233",
}

# Province / place gazetteer (lat, lng, province_en, province_th, location_th, precision)
# precision: area for a city or district, province for a province-only pin
PLACES = {
    "bangkok": (13.7563, 100.5018, "Bangkok", "กรุงเทพมหานคร", "กรุงเทพมหานคร", "area"),
    "saphan sung": (13.7700, 100.6860, "Bangkok", "กรุงเทพมหานคร", "เขตสะพานสูง กรุงเทพมหานคร", "area"),
    "salaya": (13.8010, 100.3230, "Nakhon Pathom", "นครปฐม", "ศาลายา จังหวัดนครปฐม", "area"),
    "phuket": (7.8804, 98.3923, "Phuket", "ภูเก็ต", "ภูเก็ต", "area"),
    "patong": (7.8965, 98.2965, "Phuket", "ภูเก็ต", "หาดป่าตอง ภูเก็ต", "area"),
    "patung": (7.8965, 98.2965, "Phuket", "ภูเก็ต", "หาดป่าตอง ภูเก็ต", "area"),
    "hua hin": (12.5706, 99.9588, "Prachuap Khiri Khan", "ประจวบคีรีขันธ์", "หัวหิน จังหวัดประจวบคีรีขันธ์", "area"),
    "ban krut": (11.3230, 99.5480, "Prachuap Khiri Khan", "ประจวบคีรีขันธ์", "บ้านกรูด จังหวัดประจวบคีรีขันธ์", "area"),
    "koh samui": (9.5120, 100.0130, "Surat Thani", "สุราษฎร์ธานี", "เกาะสมุย จังหวัดสุราษฎร์ธานี", "area"),
    "ko samui": (9.5120, 100.0130, "Surat Thani", "สุราษฎร์ธานี", "เกาะสมุย จังหวัดสุราษฎร์ธานี", "area"),
    "chaweng": (9.5319, 100.0610, "Surat Thani", "สุราษฎร์ธานี", "หาดเฉวง เกาะสมุย", "area"),
    "thong nai pan": (9.7790, 100.0570, "Surat Thani", "สุราษฎร์ธานี", "ทองหลาง / ทองนายพาน เกาะพะงัน", "area"),
    "koh phangan": (9.7430, 100.0270, "Surat Thani", "สุราษฎร์ธานี", "เกาะพะงัน จังหวัดสุราษฎร์ธานี", "area"),
    "koh chang": (12.0700, 102.3300, "Trat", "ตราด", "เกาะช้าง จังหวัดตราด", "area"),
    "chiang mai": (18.7883, 98.9853, "Chiang Mai", "เชียงใหม่", "เชียงใหม่", "area"),
    "chiang rai": (19.9072, 99.8308, "Chiang Rai", "เชียงราย", "เชียงราย", "area"),
    "mueang chiang rai": (19.9072, 99.8308, "Chiang Rai", "เชียงราย", "อำเภอเมืองเชียงราย", "area"),
    "pattaya": (12.9236, 100.8825, "Chon Buri", "ชลบุรี", "พัทยา จังหวัดชลบุรี", "area"),
    "muang pattaya": (12.9236, 100.8825, "Chon Buri", "ชลบุรี", "เมืองพัทยา จังหวัดชลบุรี", "area"),
    "hat yai": (7.0084, 100.4767, "Songkhla", "สงขลา", "หาดใหญ่ จังหวัดสงขลา", "area"),
    "hatyai": (7.0084, 100.4767, "Songkhla", "สงขลา", "หาดใหญ่ จังหวัดสงขลา", "area"),
    "sukhothai": (17.0170, 99.7030, "Sukhothai", "สุโขทัย", "อุทยานประวัติศาสตร์สุโขทัย", "area"),
    "sutkothai": (17.0170, 99.7030, "Sukhothai", "สุโขทัย", "อุทยานประวัติศาสตร์สุโขทัย", "area"),
    "suranari": (14.9740, 102.0830, "Nakhon Ratchasima", "นครราชสีมา", "ตำบลสุรนารี นครราชสีมา", "area"),
    "tambon suranari": (14.9740, 102.0830, "Nakhon Ratchasima", "นครราชสีมา", "ตำบลสุรนารี นครราชสีมา", "area"),
    "loei": (17.4860, 101.7220, "Loei", "เลย", "อำเภอเมืองเลย", "area"),
    "erawan": (17.4860, 101.7220, "Loei", "เลย", "ตำบลเอราวัณ อำเภอเมืองเลย", "area"),
    "utapao": (12.6799, 101.0050, "Rayong", "ระยอง", "ฐานทัพอากาศอู่ตะเภา จังหวัดระยอง", "area"),
    "udorn": (17.3860, 102.7880, "Udon Thani", "อุดรธานี", "อุดรธานี (ฐานทัพอากาศในรายงานปี 1968)", "area"),
    "andaman": (7.8, 98.2, "Phuket", "ภูเก็ต", "ทะเลอันดามัน (ใกล้ภูเก็ต)", "area"),
    "strait of malacca": (7.5, 98.0, "Phuket", "ภูเก็ต", "ช่องแคบมะละกา / ทะเลอันดามัน", "area"),
}

SHAPE_TO_CAT = {
    "light": "light_orb",
    "orb": "light_orb",
    "circle": "light_orb",
    "sphere": "light_orb",
    "flash": "light_orb",
    "fireball": "fireball",
    "triangle": "triangle",
    "chevron": "triangle",
    "disk": "disc",
    "disc": "disc",
    "oval": "disc",
    "egg": "disc",
    "teardrop": "disc",
    "formation": "formation",
    "cylinder": "cylinder_other",
    "cone": "cylinder_other",
    "rectangle": "cylinder_other",
    "changing": "unspecified",
    "unknown": "unspecified",
    "other": "unspecified",
}

# Original paraphrases (not verbatim copies of long witness text)
CUSTOM = {
    "2987": ("Twelve slow red-orange lights over Phuket on Christmas Eve",
             "สิบสองดวงไฟสีแดงส้มเคลื่อนช้าเหนือภูเก็ตคืนคริสต์มาสอีฟ",
             "A witness reported twelve slow-moving, red-orange pulsating objects over Phuket at about 10:05 on Christmas Eve 1997."),
    "5893": ("A ruler-shaped object with four steady lights near Hua Hin",
             "วัตถุคล้ายไม้บรรทัดมีไฟสี่จุดใกล้หัวหิน",
             "Near Hua Hin, Prachuap Khiri Khan, a witness described a roughly ruler-shaped, seemingly semi-transparent object with four evenly spaced, non-blinking glowing spots along the bottom, seen high in the sky at 23:00 on 1 November 1997."),
    "18768": ("Saucer-like shapes on photos taken on a Bangkok–Hong Kong flight",
              "รูปทรงคล้ายจานในภาพถ่ายระหว่างเที่ยวบินกรุงเทพฯ–ฮ่องกง",
              "A passenger on a flight from Bangkok toward Hong Kong photographed a cloud formation on 15 December 2000 and later thought one, perhaps two, saucer-like shapes appeared in frames taken after the first shot. The exact position over land or sea is not stated, so this case is not pinned to a Thai province."),
    "20465": ("A fast round glow westbound over Bangkok",
              "วงแสงกลมเคลื่อนเร็วไปทางทิศตะวันตกเหนือกรุงเทพฯ",
              "A witness in Bangkok described a round, glowing circular object moving very fast toward the west at high altitude, at about 01:30 on 19 November 2001."),
    "29788": ("Daytime triangle seen by U.S. Navy personnel",
              "วัตถุสามเหลี่ยมกลางวันโดยทหารเรือสหรัฐ",
              "A 2003 NUFORC filing says three U.S. Navy personnel saw a triangular object in a daytime sky outside a popular Thai tourist area in June 1985. The exact town is not named."),
    "35456": ("A briefly described Koh Samui night sighting",
              "รายงานสั้น ๆ จากเกาะสมุยยามค่ำ",
              "A November 2003 Koh Samui filing is recorded in the NUFORC index with almost no descriptive detail, only a dramatic claim that it was proof of an extraterrestrial visit. It is kept here as a dated, located witness report, with that lack of detail flagged."),
    "36767": ("Hundreds of slow red star-like lights over Bangkok",
              "แสงคล้ายดาวสีแดงหลายร้อยดวงลอยช้าเหนือกรุงเทพฯ",
              "On 7 May 2004 around 23:48 a Bangkok witness described hundreds of star-like objects rising slowly, looking like small red stars, visible for 10–15 minutes before they disappeared. The description is consistent with sky lanterns, though the report does not use that word."),
    "40511": ("Hundreds of red lights drifting over Bangkok",
              "แสงสีแดงหลายร้อยดวงลอยข้ามฟ้ากรุงเทพฯ",
              "On 18 August 2004 at 23:30 a Bangkok witness reported hundreds of strange red lights floating across the night sky. As with other mass red-light reports, lanterns are a common mundane comparison, but the filing itself does not settle the cause."),
    "41643": ("A large red pulsating light over Thong Nai Pan",
              "แสงแดงขนาดใหญ่กระพริบเหนือทองนายพาน",
              "On 26 December 2004 at 22:30, a group of about ten people holidaying at Thong Nai Pan on Ko Pha-ngan reported an unusually large, red, pulsating star-like object in the sky."),
    "42146": ("A line of lights in the NNW from U-Tapao air base, 1968",
              "แถวแสงทางทิศตะวันตกเฉียงเหนือจากอู่ตะเภา ปี 1968",
              "A report later filed with NUFORC describes multiple lights in a horizontal formation in the north-northwest sky, seen around 01:00 on 15 June 1968 from U-Tapao Royal Thai Air Force Base in Rayong, a major U.S. staging field during the Vietnam War era."),
    "43319": ("An orange sphere over Chiang Mai",
              "ทรงกลมสีส้มเหนือเชียงใหม่",
              "A witness reported an orange sphere in the sky above Chiang Mai at about 19:30 on 30 January 2005."),
    "48523": ("A Phuket air-traffic controller files a report",
              "พนักงานควบคุมจราจรทางอากาศภูเก็ตส่งรายงาน",
              "A person identifying themselves as a former air-traffic controller at Phuket International Airport filed a NUFORC report dated 30 June 1999 (time given as midnight, which may only mark the date). The public index line says they received a report while on duty; the full narrative sits on the NUFORC record."),
    "50463": ("More than 25 lights videotaped over Patong — lanterns suggested",
              "แสงกว่า 25 ดวงถูกถ่ายวิดีโอที่ป่าตอง — มีหมายเหตุว่าอาจเป็นโคม",
              "On 22 March 2006 at 23:30 a witness at Patong Beach, Phuket, said they took a nine-minute video of more than 25 lights travelling east over the island. A NUFORC editor's note on the index asks whether they might have been lanterns."),
    "51312": ("A bright green chevron westbound over Hat Yai",
              "แสงเขียวสว่างรูปตัววีพาดไปทิศตะวันตกเหนือหาดใหญ่",
              "A Hat Yai, Songkhla, report dated 4 July 2001 describes a bright green, highly luminous chevron-shaped light flying from east to west."),
    "53965": ("A star-like object that suddenly dived and hovered over Bangkok",
              "วัตถุคล้ายดาวที่พุ่งลงแล้วค้างเหนือกรุงเทพฯ",
              "On 13 December 2006 at 23:00 a Bangkok witness said an ordinary-looking bright star suddenly caught the eye as it sped inward at a steep angle and then hovered."),
    "54473": ("A circle compared to a movie spaceship — location not given",
              "วงกลมที่ผู้เห็นเปรียบกับยานในหนัง — ไม่ระบุสถานที่",
              "A 2 January 2007 filing from 'Thailand' compares what was seen to a well-known science-fiction film but does not name a town. It is listed without a map pin."),
    "59435": ("A long-running dawn light east of Bangkok — Venus suggested",
              "แสงยามรุ่งทางตะวันออกของกรุงเทพฯ นานเป็นเดือน — มีหมายเหตุว่าอาจเป็นดาวศุกร์",
              "A Bangkok witness described unusual lights in the eastern sky between about 04:00 and 06:00, said to have been going on for a month by 26 October 2007. A NUFORC editor's note asks whether the object was Venus."),
    "59932": ("An orange oval over the Andaman Sea off Patong",
              "วัตถุสีส้มรูปรีเหนือทะเลอันดามันหน้าป่าตอง",
              "On 13 November 2007 at 22:00 a witness at Patong Beach described an orange, oval, glowing object moving slowly east over the Andaman Sea. It then stopped, according to the index summary."),
    "70835": ("A large object low on the Koh Samui horizon",
              "วัตถุขนาดใหญ่ต่ำที่ขอบฟ้าเกาะสมุย",
              "A mid-2005 Koh Samui filing (date given as 30 June, time midnight) describes large object or objects hovering low on the horizon."),
    "79273": ("Multi-coloured dancing lights videotaped in Salaya",
              "แสงหลายสีเคลื่อนพลิ้วถูกถ่ายวิดีโอที่ศาลายา",
              "On 13 December 2010 at 22:00 a married couple in Salaya, Nakhon Pathom, reported a dancing, multi-coloured object and said they videotaped it for about five minutes."),
    "93382": ("Two orange orbs off the coast of Koh Samui",
              "ลูกแสงส้มสองดวงนอกชายฝั่งเกาะสมุย",
              "On 5 October 2012 at 21:40 a witness reported two sightings of orange orbs off the coast of Koh Samui. A second NUFORC record filed the same day is an addendum to the same event and is merged here."),
    "100377": ("Three white circular objects over southern Phuket",
               "วัตถุวงกลมสีขาวสามชิ้นเหนือภูเก็ตตอนใต้",
               "A 15 June 2007, 21:00, filing from southern Phuket describes three white, circular objects."),
    "103238": ("A bright orange sphere in a Koh Samui night sky",
               "ทรงกลมสีส้มสว่างบนฟ้าค่ำเกาะสมุย",
               "On 12 October 2013 at 21:00 a Koh Samui witness reported a bright orange sphere in the night sky."),
    "103372": ("Five bright lights over Chaweng Beach",
               "แสงสว่างห้าดวงเหนือหาดเฉวง",
               "On 19 October 2013 at 22:00 a witness reported five bright lights above Chaweng Beach, Koh Samui. The date is the same night as the annual Naga-fireball festival further north, but this report is a separate island sighting and is not assumed to be the same phenomenon."),
    "107662": ("Geometric lights over Erawan, Loei, in daylight",
               "แสงเรขาคณิตเหนือตำบลเอราวัณ จังหวัดเลย กลางวัน",
               "On 6 March 2014 at 11:15 a witness in Erawan, Mueang Loei, reported geometric lights over north-east Thailand."),
    "108977": ("A zig-zagging bright light over Udorn air base, 1968",
               "แสงสว่างเคลื่อนเป็นซิกแซกเหนือฐานทัพอากาศอุดร ปี 1968",
               "A later NUFORC filing describes a zig-zagging bright light over the U.S. air base at Udorn (Udon Thani) around 01:00 on 1 January 1968. January the first may be a placeholder date; it is recorded here exactly as NUFORC lists it."),
    "118167": ("A billboard-like white light at Ban Krut",
               "แสงขาวคล้ายป้ายไฟที่บ้านกรูด",
               "On 10 March 2015 at 06:00 a witness at Ban Krut, Prachuap Khiri Khan, described a billboard of white light."),
    "124977": ("A bright, stationary 'orbiting' object on New Year's morning — maybe a planet",
               "วัตถุสว่างนิ่งคล้ายวงโคจรเช้าวันปีใหม่ — อาจเป็นดาวเคราะห์",
               "Just after midnight on 1 January 2016 a Bangkok witness described a bright, stationary object that appeared to be in orbit. A NUFORC editor's note asks whether it was a planet near the Moon."),
    "128584": ("Five teardrop objects in a delta over Bangkok in a storm",
               "วัตถุรูปหยดน้ำห้าชิ้นเรียงสามเหลี่ยมเหนือกรุงเทพฯ ขณะพายุ",
               "On 18 July 2016 at 20:00, during a heavy thunderstorm, a visitor in Bangkok reported five teardrop- or fang-shaped objects in a delta formation."),
    "134659": ("An unidentified object from a patio near Chiang Rai airport",
               "วัตถุไม่ทราบชนิดจากระเบียงบ้านใกล้สนามบินเชียงราย",
               "On 18 June 2017 around 20:08 a witness grilling on a patio near Chiang Rai, and used to ordinary airport traffic, reported something they could not immediately identify in the dark sky. The public index line is truncated."),
    "143648": ("A triangle over Pattaya that the witnesses said was not a plane",
               "วัตถุสามเหลี่ยมเหนือพัทยา ที่ผู้เห็นย้ำว่าไม่ใช่เครื่องบิน",
               "On 2 November 2018 at 21:30 Pattaya witnesses who said they regularly see airliners from Bangkok and U-Tapao reported a craft they insisted did not look like a plane."),
    "144299": ("Two bright orange lights over Bangkok",
               "แสงส้มสว่างสองดวงเหนือกรุงเทพฯ",
               "On 5 December 2012 at 20:00 a Bangkok witness reported two bright orange lights that appeared to be far up in the night sky."),
    "154794": ("A low, quiet triangle gliding over Bangkok",
               "สามเหลี่ยมบินต่ำ เสียงเบากล้ายไถลเหนือกรุงเทพฯ",
               "On 4 April 2020 at 19:23 a Bangkok witness described a low-flying triangular object just under low cloud, without the usual jet sound, gliding from the south-west toward the east. Lights were a dull off-white, not flashing."),
    "157040": ("A fast, silent object estimated tens of metres long over Koh Samui",
               "วัตถุเงียบเคลื่อนเร็ว ประมาณยาวหลายเมตรเหนือเกาะสมุย",
               "On 14 June 2020 at 20:00 a Koh Samui witness described an object flying south-west to north-east, estimated under 1,000 feet up, very fast, silent, and perhaps 10–20 metres long."),
    "162740": ("Two rod-like, shape-shifting objects over Ko Chang",
               "วัตถุคล้ายแท่งสองชิ้นที่เปลี่ยนรูปเหนือเกาะช้าง",
               "Around 01:00 on 31 December 2002, a witness on Ko Chang described a five-minute sighting of two rod-like, shape-shifting objects that moved deliberately and then disappeared at what the witness called impossible speed."),
    "165709": ("A triangle that appeared over the sea and then overhead in Pattaya",
               "สามเหลี่ยมที่เห็นเหนือทะเลแล้วปรากฏเหนือศีรษะที่พัทยา",
               "On 22 July 2006 at 03:00 a Pattaya witness described a shape hovering over the sea, disappearing, and then appearing overhead."),
    "173726": ("A cylinder that at first looked like part of an airliner's wing",
               "ทรงกระบอกที่ตอนแรกดูคล้ายส่วนปีกเครื่องบิน",
               "On 27 November 2022 at 19:00 a traveller flying over the Strait of Malacca / Andaman Sea described an object that first seemed to be an extension of an aeroplane wing until it flew away. The report is tied to Thai airspace only loosely."),
    "176150": ("A hovering circular object over Hat Yai",
               "วัตถุวงกลมลอยค้างเหนือหาดใหญ่",
               "On 9 June 2023 at 21:21 a Hat Yai filing describes some type of flying object on hover. The NUFORC index marks the record as having media attached."),
    "176966": ("A dim, very fast egg-shaped object over Saphan Sung",
               "วัตถุทรงไข่แสงจางเคลื่อนเร็วมากที่สะพานสูง",
               "On 26 July 2023 at 20:03 a witness in Saphan Sung, Bangkok, reported a not-very-bright object travelling too fast."),
    "178233": ("A star-like oval in photographs at Sukhothai Historical Park",
               "วัตถุคล้ายดาวรูปรีในภาพถ่ายที่อุทยานประวัติศาสตร์สุโขทัย",
               "On 14 September 2023 around 15:50–15:56, two closely timed NUFORC filings from the Sukhothai UNESCO World Heritage site describe a star-like object that looked oval when a photograph was magnified. They are treated here as one event. Media is flagged on the index."),
    "179751": ("Five flying objects over Mueang Chiang Rai — birds suggested",
               "วัตถุบินห้าชิ้นเหนือเมืองเชียงราย — มีหมายเหตุว่าอาจเป็นนก",
               "On 18 December 2023 at 13:22 a Mueang Chiang Rai witness reported five flying objects. The NUFORC explanation column on the index asks whether they were birds."),
    "182848": ("Slow-turning blue and white lights over Pattaya at dawn",
               "แสงฟ้าขาวหมุนช้าเหนือพัทยาตอนรุ่ง",
               "On 4 August 2024 at 05:00 a Muang Pattaya witness described blue and white lights turning slowly."),
    "185054": ("Lights above the water in southern Thailand — no town named",
               "แสงเหนือผิวน้ำทางภาคใต้ — ไม่ระบุเมือง",
               "On 13 December 2024 at 04:10 a NUFORC report describes lights above the water in southern Thailand but does not name a province or beach. It is listed without a map pin."),
    "185675": ("Three flashing lights on a seaward horizon at Khao Niwet",
               "แสงกระพริบสามดวงบนขอบฟ้าทะเลที่เขานิเวศน์",
               "On 20 December 2024 at 23:55 a witness at a place given as Khao Niwet reported three horizontal lights flashing across the horizon on the sea, moving at various speeds. The name is not unique in Thailand and could not be geocoded with confidence, so this case has no map pin."),
    "188235": ("A yellow light moving at great speed — no place given",
               "แสงเหลืองเคลื่อนเร็วมาก — ไม่ระบุสถานที่",
               "On 10 March 2025 at 23:50 a witness described a yellow light moving at great speed but did not name a town. It is listed without a map pin."),
    "191093": ("A black sphere seen from a Hua Hin hotel pool in cloudy weather",
               "ทรงกลมสีดำจากสระโรงแรมที่หัวหินในวันที่เมฆมาก",
               "On 28 May 2025 at 16:30 a witness at a rooftop hotel pool in Hua Hin, in very cloudy weather, reported a black spot perhaps a couple of kilometres away and about a mile up. The index marks media attached."),
    "192966": ("A submarine-shaped object in a Bangkok pre-dawn sky",
               "วัตถุคล้ายเรือดำน้ำบนฟ้ากรุงเทพฯ ก่อนรุ่ง",
               "On 3 October 2025 at 03:00 a Bangkok witness said they saw a submarine-like object in the sky after getting up in the night. The index marks media attached."),
    "194130": ("A black rectangle — no place given",
               "สี่เหลี่ยมสีดำ — ไม่ระบุสถานที่",
               "On 14 November 2025 at 16:00 a NUFORC filing describes a black rectangular object but names no town. It is listed without a map pin."),
    "194486": ("A star-like moving light over Tambon Suranari",
               "แสงคล้ายดาวที่เคลื่อนที่เหนือตำบลสุรนารี",
               "On 30 November 2025 at 05:51 a witness in tambon Suranari, Nakhon Ratchasima, described an object about the apparent size of a star, only clearer, moving in one direction. Media is flagged on the index."),
    "196742": ("Multi-coloured hovering objects over Koh Samui, 2003",
               "วัตถุหลายสีลอยค้างเหนือเกาะสมุย ปี 2003",
               "On 15 July 2003 at 19:58 a visitor outside a rented house on Koh Samui reported strangely behaving, multi-coloured objects hovering in the sky. Media is flagged on the index."),
    "197577": ("A fireball-like object said to react to lasers — Ban Pho",
               "วัตถุคล้ายลูกไฟที่ผู้เห็นว่าตอบสนองต่อเลเซอร์ — ตำบลบ้านโพธิ์",
               "On 25 December 2025 at 02:42 a filing from 'tambon Ban Pho' describes a fireball-like object moving back and forth at high speed, which the witness associated with high-intensity lasers. Ban Pho is a common sub-district name in several provinces, so this case has no map pin."),
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def geocode(city: str):
    raw = city or ""
    n = norm(raw)
    n = n.replace("(thailand)", " ").replace("thailand", " ")
    n = re.sub(r"[(),.;]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    # try longest keys first
    for key, val in sorted(PLACES.items(), key=lambda kv: -len(kv[0])):
        if key in n:
            return val
    return None


def parse_occurred(s: str):
    s = (s or "").strip()
    # e.g. 12/24/1997 10:05
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if not m:
        return None, None, "unknown", s or "Date not stated"
    month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hh, mm = m.group(4), m.group(5)
    date = f"{year:04d}-{month:02d}-{day:02d}"
    time_local = f"{int(hh):02d}:{mm}" if hh is not None else None
    # midnight often means "date only"
    if time_local == "00:00":
        time_local = None
        label = datetime(year, month, day).strftime("%-d %B %Y")
        return date, None, "day", label
    if time_local:
        dt = datetime(year, month, day, int(hh), int(mm))
        label = dt.strftime("%-d %B %Y, %H:%M")
        return date, time_local, "day", label
    label = datetime(year, month, day).strftime("%-d %B %Y")
    return date, None, "day", label


def category_from_shape(shape: str, summary: str) -> str:
    sh = (shape or "").strip().lower()
    if sh in SHAPE_TO_CAT:
        return SHAPE_TO_CAT[sh]
    low = (summary or "").lower()
    if "triangle" in low:
        return "triangle"
    if "orb" in low or "sphere" in low:
        return "light_orb"
    return "unspecified"


def nuforc_explain_tag(explanation: str, summary: str):
    blob = f"{explanation or ''} {summary or ''}"
    low = blob.lower()
    if "possible lanterns" in low or "lanterns??" in low:
        return "explained", "A NUFORC editor noted that the lights may have been lanterns."
    if "sighting of venus" in low:
        return "explained", "A NUFORC editor suggested the object may have been the planet Venus."
    if "planet near moon" in low:
        return "explained", "A NUFORC editor suggested a planet near the Moon."
    if re.search(r"\bbird\??", low):
        return "explained", "A NUFORC editor suggested the objects may have been birds."
    return "witness_report", "A public witness report in the NUFORC archive. It has not been independently verified for this dashboard."


def build_nuforc(raw):
    by_id = {r["nuforc_id"]: r for r in raw if r.get("nuforc_id")}
    items = []
    seen_merge_target = set()
    for rec in raw:
        nid = rec.get("nuforc_id")
        if not nid or nid in SKIP_NUFORC:
            continue
        if nid in MERGE_INTO:
            continue
        date, time_local, prec, label = parse_occurred(rec.get("Occurred") or "")
        city = rec.get("City") or ""
        geo = geocode(city)
        custom = CUSTOM.get(nid)
        if custom:
            title, title_th, summary = custom
        else:
            title = (rec.get("Summary") or "A Thailand report in the NUFORC index")[:90]
            title_th = "รายงานจากศูนย์ NUFORC ในประเทศไทย"
            summary = "A public NUFORC index summary from a Thailand report. See the source record for the witness's own wording."
        cred, cred_note = nuforc_explain_tag(rec.get("Explanation") or "", rec.get("Summary") or "")
        lat = lng = None
        province = province_th = location_th = None
        precision = "unspecified"
        coord_note = None
        if geo:
            lat, lng, province, province_th, location_th, precision = geo
            coord_note = "Geocoded from the place name on the NUFORC index, not from a measured bearing or GPS fix."
        # special cases: no reliable pin
        no_pin_ids = {"18768", "29788", "54473", "185054", "185675", "188235", "194130", "197577", "173726"}
        if nid in no_pin_ids:
            # 173726 is over water; keep loose andaman coords? Brief says don't invent. Safer no pin.
            lat = lng = None
            precision = "unspecified"
            coord_note = "The report does not name a town that can be geocoded with confidence, so it is not placed on the map."
            if nid == "173726":
                province, province_th = None, None
                coord_note = "The witness was on a flight over the Strait of Malacca / Andaman Sea. No island or airport is named, so there is no map pin."
            if nid == "18768":
                coord_note = "Photographs were taken on a flight from Bangkok toward Hong Kong. The exact location is not stated."

        sources = [{
            "name": "NUFORC public report",
            "url": rec.get("source_url") or f"https://nuforc.org/sighting/?id={nid}",
        }, {
            "name": "NUFORC Thailand index (Wayback Machine, 13 May 2026)",
            "url": "https://web.archive.org/web/20260513100815/https://nuforc.org/subndx/?id=cThailand",
        }]
        # merged addenda
        for other, target in MERGE_INTO.items():
            if target == nid and other in by_id:
                sources.append({
                    "name": f"NUFORC addendum ({other})",
                    "url": f"https://nuforc.org/sighting/?id={other}",
                })

        item = {
            "id": f"nuforc-{nid}",
            "title": title,
            "title_th": title_th,
            "date": date,
            "date_label": label,
            "date_precision": prec if date else "unknown",
            "time_local": time_local,
            "location_name": re.sub(r"\s+", " ", city).strip() or "Location not stated",
            "location_name_th": location_th or (city or "ไม่ระบุสถานที่"),
            "province": province,
            "province_th": province_th,
            "lat": lat,
            "lng": lng,
            "coord_precision": precision if lat is not None else "unspecified",
            "coord_note": coord_note,
            "category": category_from_shape(rec.get("Shape") or "", rec.get("Summary") or ""),
            "shape": rec.get("Shape") or None,
            "credibility": cred,
            "credibility_note": cred_note,
            "summary": summary,
            "summary_th": None,  # filled below for key ones; UI can fall back to EN
            "sources": sources,
            "photos": [],
            "media_in_source": (rec.get("Media") or "").strip().upper() == "Y",
            "nuforc_id": nid,
            "explanation": (rec.get("Explanation") or "").strip() or None,
        }
        # Thai summaries: use title_th + short generic if no custom TH paragraph stored
        # Custom third field is English only; add a concise TH companion from title
        item["summary_th"] = (
            "รายงานพยานที่ส่งถึงศูนย์รายงานยูเอฟโอแห่งชาติสหรัฐ (NUFORC) "
            "ข้อความนี้เรียบเรียงจากสารบัญสาธารณะ ไม่ได้คัดลอกคำให้การเต็ม และยังไม่ได้รับการตรวจสอบอิสระในแดชบอร์ดนี้"
        )
        items.append(item)
    return items


def iso_now():
    # Asia/Bangkok
    return datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S%z")


def sort_key(it):
    d = it.get("date") or "0000-00-00"
    # month-only dates sort mid-month
    if re.fullmatch(r"\d{4}-\d{2}", d):
        d = d + "-15"
    t = it.get("time_local") or "00:00"
    return (d, t, it.get("id") or "")


def assign_case_numbers(items):
    items.sort(key=sort_key)
    for i, it in enumerate(items, 1):
        it["case_no"] = f"TH-{i:04d}"
        it["year"] = int(it["date"][:4]) if it.get("date") and it["date"][:4].isdigit() else None
    return items


def main():
    raw = json.loads((PIPELINE / "nuforc_raw.json").read_text(encoding="utf-8"))
    curated = json.loads((PIPELINE / "curated_events.json").read_text(encoding="utf-8"))
    nuforc_items = build_nuforc(raw)
    curated_items = []
    for ev in curated:
        item = {
            "id": ev["id"],
            "title": ev["title"],
            "title_th": ev["title_th"],
            "date": ev["date"],
            "date_label": ev["date_label"],
            "date_precision": ev.get("date_precision") or "day",
            "time_local": ev.get("time_local"),
            "location_name": ev["location_name"],
            "location_name_th": ev.get("location_name_th"),
            "province": ev.get("province"),
            "province_th": ev.get("province_th"),
            "lat": ev.get("lat"),
            "lng": ev.get("lng"),
            "coord_precision": ev.get("coord_precision") or "area",
            "coord_note": ev.get("coord_note"),
            "category": ev["category"],
            "shape": ev.get("shape"),
            "credibility": ev["credibility"],
            "credibility_note": ev.get("credibility_note"),
            "summary": ev["summary"],
            "summary_th": ev.get("summary_th"),
            "explanation": ev.get("explanation"),
            "explanation_th": ev.get("explanation_th"),
            "sources": ev.get("sources") or [],
            "photos": ev.get("photos") or [],
            "media_in_source": bool(ev.get("photos")),
        }
        curated_items.append(item)

    all_items = assign_case_numbers(nuforc_items + curated_items)

    doc = {
        "generated_at": iso_now(),
        "timezone": "Asia/Bangkok",
        "title": "Thailand UFO Files",
        "disclaimer": (
            "Entries are unverified reports aggregated from public sources. "
            "They are not proof of extraterrestrial craft. Many have mundane explanations "
            "(meteors, satellites, the ISS, weather balloons, sky lanterns, clouds, rocket debris). "
            "Coordinates are geocoded from named places and are often approximate. "
            "Nothing here was invented: if a source was blocked or incomplete, the case was omitted or labelled honestly."
        ),
        "methodology": {
            "nuforc": (
                "NUFORC's live site is behind a Cloudflare challenge, so the Thailand index was read from a "
                "public Wayback Machine snapshot dated 13 May 2026 (https://web.archive.org/web/20260513100815/"
                "https://nuforc.org/subndx/?id=cThailand). Individual report URLs still point at nuforc.org. "
                "Two addendum records were merged with their parent events. A creature report and a filing "
                "in which the writer said they had not seen a UFO were omitted."
            ),
            "news": (
                "Thai and English news and official science comments were added only when a dated article could be read. "
                "Naga fireball years are included only when a post-event count or a contemporary photograph exists. "
                "Festival preview articles were not treated as confirmation."
            ),
            "skipped": (
                "nuforc.org (Cloudflare challenge; used Wayback instead). "
                "Reddit public JSON returned an HTML interstitial, so no Reddit posts were added. "
                "MUFON public data was not reachable as an open dump. "
                "Some Thai news photo-galleries returned 404. Robots and access walls were not circumvented."
            ),
            "photos": (
                "Only Wikimedia Commons photographs (CC BY-SA 4.0, attributed) and clearly labelled generated "
                "illustrations are hosted. News photographs are not copied; cases link back to the article."
            ),
        },
        "counts": {},
        "sightings": all_items,
    }
    cred = {}
    cat = {}
    src = {}
    photos = 0
    mapped = 0
    for it in all_items:
        cred[it["credibility"]] = cred.get(it["credibility"], 0) + 1
        cat[it["category"]] = cat.get(it["category"], 0) + 1
        if it.get("photos"):
            photos += 1
        if it.get("lat") is not None:
            mapped += 1
        for s in it.get("sources") or []:
            name = s.get("name") or "unknown"
            key = "NUFORC" if "NUFORC" in name else name.split(",")[0][:60]
            src[key] = src.get(key, 0) + 1
    doc["counts"] = {
        "total": len(all_items),
        "with_coordinates": mapped,
        "with_hosted_photos": photos,
        "by_credibility": cred,
        "by_category": cat,
        "by_source_family": src,
        "nuforc": len(nuforc_items),
        "curated_news_and_naga": len(curated_items),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", OUT, "cases", len(all_items), "mapped", mapped, "photos", photos)
    print("credibility", cred)
    print("category", cat)
    years = sorted({it["year"] for it in all_items if it.get("year")})
    print("year range", years[0], years[-1], "n_years", len(years))


if __name__ == "__main__":
    main()
