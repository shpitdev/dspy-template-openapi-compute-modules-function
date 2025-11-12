"""
Generate synthetic training/test data for the Ozempic classifier example.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data/ae-pc-classification"  # TODO confirm this is correct
TRAIN_FILE = DATA_DIR / "train.json"
TEST_FILE = DATA_DIR / "test.json"

# Transcription artifacts to make complaints sound more realistic
TRANSCRIPTION_FILLERS = [
    "um",
    "uh",
    "you know",
    "like",
    "I mean",
    "so",
    "well",
    "actually",
]
PAUSE_MARKERS = ["...", ".", ",", " - "]


def add_transcription_artifacts(text: str, intensity: float = 0.3) -> str:
    """Add realistic transcription artifacts to make text sound like a phone call transcript."""
    words = text.split()
    result = []

    for i, word in enumerate(words):
        # Occasionally add filler words
        if random.random() < intensity * 0.15 and i > 0:
            if random.random() < 0.5:
                result.append(random.choice(TRANSCRIPTION_FILLERS))

        result.append(word)

        # Occasionally add pauses or incomplete sentences
        if random.random() < intensity * 0.1:
            if random.random() < 0.3:
                result.append(random.choice(PAUSE_MARKERS))

    return " ".join(result)


def generate_training_data():
    """Generate labeled training examples for Ozempic complaints."""

    training_data = [
        # Adverse Events (10 examples)
        {
            "complaint": add_transcription_artifacts(
                """So, um, I need to report something about my patient. This is Dr. Sarah Chen calling from the internal medicine clinic. Patient is a 52-year-old woman, she's been my patient for about three years now. She has type 2 diabetes, hypertension, and she's been struggling with her weight. Her A1C was running around 7.8, which isn't terrible but we wanted to get it lower. So about a month ago, we decided to start her on Ozempic. It was the 0.5 milligram dose, weekly injection. She was really excited about it, you know, because she'd heard all the success stories about weight loss and blood sugar control. Patient started Ozempic, it was the 0.5 milligram dose, weekly injection. This was about three weeks ago, maybe a little more. I want to say it was the first week of October, and now we're at the end of October. So yeah, about three weeks. And after three weeks, they developed severe nausea and vomiting. Like, really severe. The patient called me on a Friday afternoon, and she sounded terrible. She said she'd been vomiting since Wednesday, so for about two days straight. She couldn't keep anything down, not even water. She tried drinking small sips of water, but even that came right back up. The patient called me, you know, in distress. She was really scared because she'd never experienced anything like this before. They were dehydrated, couldn't eat, lost about eight pounds in just a few days. I mean, this is not normal weight loss, this is from the vomiting. Eight pounds in three days is way too fast, and it's clearly from dehydration and not being able to eat. I advised them to stop the medication immediately and come in for evaluation. I told her to come to the clinic right away, but she was too weak to drive, so her husband brought her in. When she got here, she looked terrible - pale, weak, just really sick. We did labs, their electrolytes were off, they needed IV fluids. Her sodium was low, her potassium was low, her BUN and creatinine were elevated, which suggested dehydration. We started her on IV fluids right there in the clinic, and I sent her to the emergency room for more aggressive hydration. She ended up getting two liters of IV fluids in the ER, and they monitored her for a few hours. This is clearly an adverse reaction to the Ozempic. The timing is too coincidental - started the medication, three weeks later, severe GI symptoms. We've ruled out other causes. The patient had no history of GI issues before this. No food poisoning, no stomach flu going around, nothing. She hadn't changed her diet, hadn't started any other new medications. The only thing that changed was starting the Ozempic. I'm documenting this as an adverse event because it required medical intervention and the patient had to discontinue the medication. She's not going to continue with it, obviously. The patient is doing better now that they've stopped, but it took about a week for the symptoms to fully resolve. She's back to her baseline now, but she's really shaken up by the whole experience. I'm concerned about trying other GLP-1 agonists with her because this reaction was so severe. We're going to have to find another approach to managing her diabetes and weight.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports patient experiencing adverse drug reactions (nausea, vomiting) following Ozempic administration.",
        },
        {
            "complaint": add_transcription_artifacts(
                """Hi, this is Dr. Martinez calling about a patient complaint. Um, I have a patient who's been on Ozempic for about two months now. They came in last week because they noticed, you know, a lump in their neck. Like, they were feeling around and found this hard lump on the right side. So I examined them and found a thyroid nodule, it's about two centimeters. We did an ultrasound and, um, there are some concerning features. The radiologist said it has microcalcifications and irregular borders, which are, you know, red flags for malignancy. The patient is really worried, obviously. They're asking if this could be related to the Ozempic. I mean, I know there's a black box warning about thyroid C-cell tumors in rodents, but in humans it's less clear. However, the timing is suspicious - they started Ozempic two months ago, and now we have this nodule. We're doing a fine needle aspiration next week to check for cancer. I'm documenting this as a potential adverse event because, you know, we can't rule out the connection, and the patient is experiencing a serious medical finding that requires investigation. The patient is understandably very anxious about this whole situation.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes potential serious adverse reaction (thyroid nodule) possibly related to semaglutide use, requires medical evaluation.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is a patient calling about, um, a serious issue. So I've been on Ozempic for about a month, this was my fourth injection. I did it on Tuesday morning, and by Tuesday night I had this terrible, terrible abdominal pain. Like, the worst pain I've ever felt. It was in my upper abdomen, radiating to my back. I couldn't sleep, couldn't eat, couldn't do anything. My wife made me go to the emergency room on Wednesday. They did blood work and my amylase was, like, 450, which they said is really high. Normal is under 100. And my lipase was also elevated. The ER doctor diagnosed me with pancreatitis and admitted me to the hospital. I was there for three days on IV fluids and pain meds. They did a CT scan and confirmed it was pancreatitis. The doctors asked me about medications and when I told them about Ozempic, they said that could definitely be the cause. I've never had pancreatitis before, I don't drink alcohol, I don't have gallstones. The only thing that changed was starting this medication. I'm really upset because I was doing well with my blood sugar, but now I'm scared to take it again. The hospital doctor said I should definitely report this as an adverse event.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious adverse event (pancreatitis) with hospitalization following Ozempic use, confirmed by lab findings.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling as a healthcare provider about my patient. Patient is a 68-year-old woman on Ozempic 1 milligram weekly. She came into my office yesterday complaining of extreme fatigue and dizziness. She said she's been feeling this way for about a week, but yesterday morning it got really bad. She almost passed out when she stood up. So I checked her blood sugar right there in the office and it was 45 milligrams per deciliter. That's dangerously low. Normal is 70 to 100. She was diaphoretic, confused, shaky. I gave her glucose tablets immediately and her sugar came up to 85, but she was still symptomatic. I sent her to the emergency room because hypoglycemia that severe needs monitoring. She's on Ozempic and also metformin, but she's been on metformin for years without issues. The Ozempic is new, started about six weeks ago. The patient said she's been eating less because of the nausea from Ozempic, which probably contributed, but the medication itself can cause hypoglycemia, especially when combined with other diabetes drugs. The ER kept her overnight for observation. This is definitely an adverse event - the medication caused or contributed to a serious hypoglycemic episode requiring emergency care.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes hypoglycemic event requiring emergency care, a known adverse reaction to GLP-1 agonists.",
        },
        {
            "complaint": add_transcription_artifacts(
                """Hi, um, I need to report something that happened with my Ozempic injection. So I started Ozempic three weeks ago, and I've been doing the injections in my thigh, rotating sides. Last week, after my third injection, the injection site got really red and swollen. Like, really swollen, probably three inches across. And it was hot to touch and really painful. I put ice on it and took some ibuprofen, but it didn't help much. After a couple days, it started oozing pus, which was gross. I called my doctor and they told me to come in. When I got there, the nurse practitioner said it looked infected. She took a swab and started me on antibiotics. The culture came back positive for staph infection. I had to take oral antibiotics for ten days, and the infection finally cleared up, but it left a scar. The doctor said this could be from improper injection technique or contamination, but I've been following the instructions exactly. I clean the site with alcohol, use a new needle every time, everything. This has never happened with any other medication I've injected. I'm worried about injecting again because I don't want another infection.""",
                0.4,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports adverse reaction at injection site with infection, a medical complication from drug administration.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is really embarrassing to talk about, but I need to report this. I've been on Ozempic for six weeks now, and I've had persistent diarrhea and stomach cramps the entire time. Like, every single day. It's not getting better, it's actually getting worse. I'm having diarrhea three, four times a day, sometimes more. And the stomach cramps are constant, they wake me up at night. I've lost fifteen pounds, but not in a good way - I'm losing weight because I can't eat anything without it going straight through me. I'm afraid to eat because I know what's going to happen. I've tried Imodium, I've tried changing my diet, nothing helps. My doctor said this is a common side effect and should improve, but it's been six weeks and it's not improving. I'm missing work because I can't be away from a bathroom. I'm dehydrated all the time, I feel weak and tired. This is really affecting my quality of life. I don't know if I can keep taking this medication if this continues. My doctor wants me to try reducing the dose, but I'm already on the lowest dose. I think this is a serious adverse effect that needs to be documented.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes ongoing gastrointestinal adverse effects impacting patient's nutritional status and quality of life.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about my patient who's on Ozempic. Patient is a 72-year-old man with type 2 diabetes and chronic kidney disease, baseline creatinine was 1.0. He started Ozempic about two months ago. Last week he came in for routine labs, and his creatinine had jumped to 3.2. That's a significant acute kidney injury. His GFR dropped from 60 to 18. He's been having a lot of GI side effects from the Ozempic - nausea, vomiting, diarrhea - and I think he got dehydrated. He's an older patient, lives alone, and I don't think he was drinking enough fluids. The dehydration from the GI side effects likely caused or contributed to the acute kidney injury. We stopped the Ozempic immediately and started aggressive hydration. His creatinine is starting to come down, but it's going to take time. This is a serious adverse event - acute kidney injury requiring medical intervention and medication discontinuation. The patient is doing better now, but we're monitoring his kidney function closely. I'm documenting this because the medication's side effects led to a serious complication.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious adverse event (acute kidney injury) potentially related to Ozempic-induced dehydration.",
        },
        {
            "complaint": add_transcription_artifacts(
                """Oh my god, this was terrifying. So I did my Ozempic injection yesterday morning, and within maybe ten minutes, I started getting hives all over my body. Like, everywhere. My arms, my legs, my chest, my back. And then my face started swelling up, especially around my eyes and lips. My throat started feeling tight, and I was having trouble breathing. I have an EpiPen because I'm allergic to shellfish, so I used it immediately. My husband drove me to the emergency room. By the time we got there, maybe fifteen minutes later, I was having full-blown anaphylaxis. They gave me more epinephrine, steroids, antihistamines, the whole works. I was in the ER for about six hours before they felt comfortable sending me home. The ER doctor said this was definitely an allergic reaction to the Ozempic. I've never had an allergic reaction to any medication before. I'm really scared now. I have two more pens at home that I obviously can't use. I need to know if this is something that happens with this medication, because this was really serious. I could have died if I didn't have that EpiPen.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes serious allergic reaction (anaphylaxis) requiring emergency treatment following drug administration.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a vision problem that started after I began Ozempic. So I've been diabetic for about ten years, and I've had some mild diabetic retinopathy, but it was stable. My eye doctor checks it every year, and it hadn't changed in three years. I started Ozempic 2 milligrams about three months ago, and my blood sugar has been really good - my A1C dropped from 8.5 to 6.8, which is great. But about a month ago, my vision started getting blurry. I thought maybe I just needed new glasses, so I went to the eye doctor. He did a full exam and found that my diabetic retinopathy has gotten significantly worse. He said it's progressed from mild to moderate-severe in just a few months. There are new blood vessels forming, which is bad. He said this can happen when blood sugar drops too quickly - it's called the early worsening phenomenon. The rapid improvement in my diabetes actually made my eye disease worse temporarily. I'm going to need laser treatment now, which I didn't need before. The eye doctor said this is a known risk with rapid glucose control, but it's still really concerning. My vision is noticeably worse, and I'm worried about permanent damage.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports worsening of diabetic retinopathy possibly related to rapid glucose control from Ozempic, a known risk.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is really hard for me to talk about, but I need to report what happened. I started Ozempic about two months ago for my diabetes and weight loss. At first, everything seemed fine. But after about six weeks, I started feeling really down. Like, really depressed. I've never had depression before in my life. I've always been a pretty happy person. But this was different - I felt hopeless, worthless, like there was no point to anything. I stopped wanting to do things I used to enjoy. I couldn't sleep, but I also couldn't get out of bed. And then, um, I started having thoughts about hurting myself. Like, really serious thoughts. I was planning how I would do it. My wife noticed something was wrong and made me see my doctor. My doctor immediately sent me to the psychiatric emergency room. I was admitted to the psychiatric unit and stayed there for five days. They started me on antidepressants and stopped the Ozempic. The psychiatrist said this could be related to the medication, though it's not common. I'm doing better now, but I'm still on antidepressants and seeing a therapist. I'm really scared this was caused by the Ozempic. I want to make sure this gets reported so other people know this can happen.""",
                0.4,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious psychiatric adverse events requiring hospitalization, potentially related to medication use.",
        },
        # Nuanced/Edge Cases - Adverse Events (5 examples)
        {
            "complaint": add_transcription_artifacts(
                """So I'm calling because I'm not really sure what category this falls into, but I think it's important to report. My name is Robert, I'm 48 years old, and I've been on Ozempic for about four months now. I started it because I have type 2 diabetes and I was really struggling with my weight. My doctor recommended it, and I was hopeful it would help. The first couple of months were actually pretty good - I lost about fifteen pounds, my blood sugar improved, I felt okay. But then about a month ago, I started having these weird episodes. Like, I'll be fine, sitting at my desk working, and then suddenly I'll get really dizzy and lightheaded. My heart starts racing, and it feels like my heart is going to beat out of my chest. It's really scary when it happens. This happens maybe once or twice a week, usually in the afternoon, but sometimes in the evening too. The episodes last maybe ten or fifteen minutes, and then I feel okay again, but really tired afterward. At first I thought maybe it was just stress or anxiety, but it kept happening. So I went to my cardiologist, Dr. Patel. He did an EKG, and he found that I'm having episodes of atrial fibrillation. That's when your heart beats irregularly. I've never had heart problems before, no family history of heart disease, nothing. I've always been pretty healthy, you know, other than the diabetes. The timing is suspicious because it started about a month after I began Ozempic. But here's the thing - I'm also under a lot of stress at work. We've had some major projects going on, deadlines, that kind of thing. And I've been drinking more coffee lately, like three or four cups a day, because I've been feeling really fatigued since starting the Ozempic. The fatigue is another thing - I'm tired all the time, which is weird because I'm sleeping okay. So I don't know if it's the medication, or the stress, or the caffeine, or some combination of all three. My cardiologist said it could be related to the medication, but he's not 100% sure. He said there are case reports of GLP-1 agonists causing cardiac arrhythmias, but it's not super common. He started me on a beta blocker, metoprolol, which helps some - the episodes are less frequent and less intense - but I'm still having them. I'm still having episodes maybe once a week now instead of twice. I'm documenting this because even though we're not certain it's the Ozempic, the timing suggests it could be related. And it's a serious enough problem that I think it needs to be reported. I'm not sure if I should stop the medication or not - my diabetes is doing so well on it, but these heart episodes are really concerning. My doctor and I are still trying to figure out what to do.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports cardiac symptoms temporally related to Ozempic initiation, though causality is uncertain - still classified as adverse event due to timing and medical significance.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I need to report something that happened, but I'm not sure if it's really an adverse event or just bad luck. So I've been on Ozempic for about three months, and I've been having a lot of GI side effects - nausea, some vomiting, diarrhea. It's been manageable, but annoying. Last week, I was vomiting pretty badly, and I guess I aspirated some of it into my lungs. I ended up with aspiration pneumonia. I was hospitalized for four days on IV antibiotics. The doctors said the vomiting from the Ozempic contributed to the aspiration. But I also have GERD, which I've had for years, so it's not like the Ozempic is the only factor. But the vomiting definitely made it worse. I'm better now, but it was scary. I'm not sure if this counts as an adverse event since it's more of a complication from the side effects, but I think it's important to document because the medication's side effects led to a serious infection.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes serious complication (aspiration pneumonia) resulting from GI adverse effects of Ozempic, even if underlying GERD was a contributing factor.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is a complicated situation. My patient has been on Ozempic for about five months, and she's been doing really well with her blood sugar and weight loss. But about a month ago, she started complaining of severe right upper quadrant pain. We did an ultrasound and found gallstones. She ended up needing surgery to remove her gallbladder. Now, I know that rapid weight loss can cause gallstones, and she's lost about thirty pounds on the Ozempic. So it's not directly the medication causing the gallstones, but the medication caused the weight loss which led to the gallstones. The patient is asking if this is an adverse event, and I think technically it is, because it's an indirect consequence of the medication. She needed surgery, which is a serious intervention. I'm documenting this because even though it's indirect, the medication's effect (weight loss) caused a serious medical problem requiring surgery.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious adverse event (cholelithiasis) requiring surgical intervention, indirectly caused by medication-induced rapid weight loss.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about my patient who's having a really hard time. She's been on Ozempic for about two months, and she's been experiencing severe hair loss. Like, she's losing handfuls of hair in the shower, it's coming out when she brushes it, it's everywhere. She's really distressed about it. Her primary care doctor diagnosed it as telogen effluvium, which is hair loss that can happen after stress or major changes to the body. The doctor thinks it's related to the rapid weight loss from Ozempic - she's lost about twenty-five pounds in two months, which is a lot. So it's not a direct adverse effect of the medication itself, but rather an indirect effect from the weight loss the medication causes. The patient is really upset because she's losing her hair, and it's affecting her self-esteem. She's asking if she should stop the medication, but her blood sugar is so much better. This is a quality of life issue that's indirectly related to the medication. I'm documenting this because even though it's indirect, it's a significant adverse effect on the patient's wellbeing.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports adverse effect (alopecia) indirectly related to medication-induced rapid weight loss, affecting patient quality of life.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So this is kind of a gray area, but I think it needs to be reported. My patient has been on Ozempic for about three months, and he's been having constipation. Like, really bad constipation. He's been taking laxatives, but they're not helping much. Last week, he came into the ER with severe abdominal pain and distension. We did a CT scan and found a partial bowel obstruction. He was admitted for three days, had to have an NG tube, the whole thing. Now, constipation is a known side effect of Ozempic, and severe constipation can lead to bowel obstruction. But the patient also has a history of diverticulosis, which can predispose to obstruction. So it's not entirely clear if this is directly from the Ozempic or if the Ozempic just made an underlying condition worse. But the timing is suspicious, and the constipation from Ozempic definitely contributed. I'm documenting this as an adverse event because the medication's side effect led to a serious complication requiring hospitalization.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious GI complication (bowel obstruction) requiring hospitalization, potentially related to Ozempic-induced constipation.",
        },
        # Product Complaints (10 examples)
        {
            "complaint": add_transcription_artifacts(
                """Hi, I need to report a problem with my Ozempic pen. So I got a new pen last week, and when I tried to use it, it won't inject. Like, I can dial the dose - I can turn the dial and it clicks and shows the dose on the counter. But when I press the injection button, nothing happens. No medication comes out at all. I've tried it three times now, same thing every time. I've used Ozempic pens before, so I know how to use them. I'm following the same steps I always do - attach the needle, dial the dose, inject. But this pen just won't work. The button depresses, but no medication comes out. I'm really frustrated because I've wasted three doses now, and these pens are expensive. I called my pharmacy and they said I need to report this to the manufacturer. The pen seems defective - like there's something wrong with the internal mechanism. I haven't had any adverse effects because I haven't actually gotten any medication from it, but I'm missing doses which isn't good for my diabetes control.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes mechanical malfunction of the pen device, not a patient safety issue but a product quality defect.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. The dose counter is stuck. Like, it's stuck between 0.5 and 1.0 milligrams. I can't tell what dose I'm actually getting. I try to dial it, and it moves a little bit, but then it gets stuck. It won't go to exactly 0.5 or exactly 1.0, it's just stuck in between. I'm really worried because I don't know if I'm getting too much medication or too little. I've tried turning it different ways, but it's just stuck. The pen mechanism appears to be broken. I haven't used it yet because I'm afraid of getting the wrong dose. I called my doctor and they said not to use it and to get a replacement. But I want to report this because this is a quality control issue. If the dose counter doesn't work, people could get the wrong dose, which could be dangerous. I'm documenting this as a product complaint because it's a defect in the device itself.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports product defect with dose counter mechanism affecting accurate dosing but no adverse patient reaction mentioned.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I received my Ozempic pen in the mail yesterday, and when I opened the box, the cap on the pen was already broken. Like, it was cracked and partially detached. The packaging itself was also damaged - the outer box was dented and torn in one corner. I'm really concerned about sterility. If the cap is broken, the pen might not be sterile anymore. I haven't used it because I'm worried about contamination. I called my pharmacy and they said it was probably damaged during shipping, but that doesn't make me feel better. If the packaging is compromised, the medication could be contaminated. I'm not going to use this pen - I'm going to ask for a replacement. But I wanted to report this because this is a quality issue. The product should arrive intact and sterile. I'm documenting this as a product complaint because it's a packaging and shipping issue that affects product quality.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes packaging and shipping damage raising sterility concerns, a product quality issue without patient harm reported.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I have a problem with the needles that came with my Ozempic pen. So I got a new pen last week, and it came with a box of needles. But the needles won't attach properly to the pen. Like, I try to screw them on, but they don't fit right. They're loose, or they won't thread correctly. I've tried multiple needles from the box, and none of them fit. I've used Ozempic before with different needles, and they worked fine. So I know it's not user error - there's something wrong with these specific needles. They seem like they might be the wrong size or thread pattern. I can't use the pen because I can't attach a needle to it. I called my pharmacy and they're going to send me replacement needles, but I wanted to report this because this is a manufacturing defect. If needles don't fit properly, people could have problems injecting, or the needle could come loose during injection, which could be dangerous. This is definitely a product quality issue.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports manufacturing defect with needle compatibility, a product quality issue not involving patient adverse effects.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is really frustrating. So I got a new Ozempic pen, and when I tried to use it, it leaked medication all over. Like, I attached the needle, dialed the dose, and when I inserted the needle and pressed the button, medication started leaking out around the needle attachment site. I lost probably half the dose. This is actually the second pen I've had this problem with. The first time, I thought maybe I did something wrong, but this time I was really careful and it still happened. The medication is expensive, and I'm wasting doses. I'm also worried that I'm not getting the full dose, which could affect my blood sugar control. I called my pharmacy and they're sending me a replacement, but I'm concerned that there's a quality control issue with these pens. If the pen leaks, people aren't getting their full dose, which could be a problem. I'm documenting this as a product complaint because it's a defect in the pen mechanism that's causing medication waste.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes repeated product defect causing medication waste, a quality issue without reported patient harm.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I received my Ozempic pen, and when I opened the box, the instructions are in Spanish. But I don't speak Spanish. I speak English. I can't understand how to use the pen because I can't read the instructions. I called my pharmacy and they said this is a labeling error - I should have received English instructions. They're going to send me the correct instructions, but I'm concerned about this. What if someone who doesn't speak English uses the pen incorrectly because they can't read the instructions? This could be dangerous. I'm also wondering if there are other labeling errors - like, is the expiration date correct? Is the dose information correct? I haven't used the pen yet because I want to make sure I understand how to use it correctly. This is a regulatory compliance issue. The product should have instructions in the correct language for the market it's being sold in. I'm documenting this as a product complaint because it's a labeling error that could affect patient safety.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports labeling error with incorrect language instructions, a regulatory compliance issue without adverse patient event.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I picked up my Ozempic pen from the pharmacy yesterday, and when I got home, I noticed the box was warm. Like, not cold at all. Ozempic is supposed to be refrigerated, right? I asked the pharmacist about it, and they said the pen arrived at the pharmacy but it wasn't refrigerated. The shipping box didn't have ice packs or anything. The pharmacist said the medication might be ineffective now because it wasn't kept cold. I'm really concerned because I don't know if the medication is still good. I haven't used it yet - I'm waiting to hear back from my doctor about whether I should use it or get a replacement. But I wanted to report this because this is a cold chain failure. If the medication isn't stored properly, it might not work, which could affect my blood sugar control. This is a product quality issue - the medication should be shipped and stored at the correct temperature. I'm documenting this as a product complaint because it's a storage and shipping issue that affects product quality.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes cold chain failure affecting product quality and potency, not a direct adverse reaction to the medication.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I have a problem with the labeling on my Ozempic pen. The expiration date is smudged and unreadable. Like, I can see there's something printed there, but I can't tell what it says. It's all blurry and smeared. I can't tell if the pen is still good to use or if it's expired. I called my pharmacy and they said they can't tell either from their records, but they'll send me a replacement. But I'm concerned about this because expiration dates are important for medication safety and effectiveness. If people can't read the expiration date, they might use expired medication, which could be ineffective or even dangerous. Or they might throw away good medication unnecessarily. This is a quality control issue with the labeling. I'm documenting this as a product complaint because it's a labeling defect that affects product usability and safety.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports labeling defect with illegible expiration date, a quality control issue affecting product usability.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about something I noticed in my Ozempic pen. So I got a new pen, and when I looked at it, I can see there are particles floating in the solution. Like, little specks or something. The solution should be clear, right? But this looks cloudy or has particles in it. I haven't used it yet because I'm concerned about contamination. What if those particles are bacteria or something? Or what if it's a manufacturing defect? I called my doctor and they said not to use it and to get a replacement. I'm going to return it to the pharmacy. But I wanted to report this because this is a quality concern. If there are visible particles in the medication, that suggests contamination or a manufacturing problem. This could be dangerous if someone uses it. I'm documenting this as a product complaint because it's a visible quality issue that suggests contamination or manufacturing defect.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes visible contamination or particulate matter indicating potential manufacturing defect, reported before use.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I got a new Ozempic pen, and the dose selector is really hard to turn. Like, extremely stiff. It takes a lot of force to dial up the dose. I'm worried I'm going to break it or something. I've used Ozempic pens before, and they were never this hard to turn. This is different from my previous pens - those were smooth and easy to dial. This one is really difficult. I'm concerned that if it's this hard to turn, maybe the mechanism is broken or defective. What if it doesn't deliver the right dose because the mechanism is stuck or damaged? I haven't used it yet because I'm worried about getting the wrong dose. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a quality issue. The pen should work smoothly and easily. If it's hard to operate, people might have trouble using it correctly, or they might not be able to use it at all. This is a mechanical defect that affects usability.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports mechanical defect with pen operation affecting ease of use, a product quality issue without patient harm.",
        },
        # Nuanced/Edge Cases - Product Complaints (5 examples)
        {
            "complaint": add_transcription_artifacts(
                """So this is kind of confusing. I got my Ozempic pen, and when I looked at it, the box says 0.5 milligrams, but the pen itself is labeled 1.0 milligrams. Like, there's a mismatch between the box label and the pen label. I don't know which one is correct. I called my pharmacy and they said they dispensed 0.5 milligrams, so that's what should be in there. But the pen says 1.0 milligrams. I'm really confused and concerned. What if I use it and get the wrong dose? That could be dangerous. I haven't used it yet - I'm waiting to hear back from my doctor about what to do. But I wanted to report this because this is a labeling error. It could be a pharmacy dispensing error, or it could be a manufacturing labeling problem. Either way, it's a product identification issue that could affect patient safety. I'm documenting this as a product complaint because the labeling mismatch makes it unclear what dose the patient is actually getting.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports labeling mismatch or dispensing error, a product identification issue without patient use or harm.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. So the injection button is stuck. Like, completely stuck. I can't depress it at all, no matter how hard I push. I've tried everything - I've tried pushing it straight down, I've tried twisting it, nothing works. It's like it's frozen in place. I can dial the dose fine, but I can't actually inject because the button won't move. This is a brand new pen, I just opened it. I'm completely unable to use it. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a mechanical failure. If the button doesn't work, people can't use the pen at all. This is a product defect that prevents use of the medication. I'm documenting this as a product complaint because it's a device malfunction that makes the product unusable.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes device mechanical failure preventing use, a product defect without adverse patient reaction.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I got my Ozempic pen, and when I looked at the solution inside, it looks cloudy instead of clear. Like, it's not transparent like it should be. It looks milky or hazy. I haven't used it yet because I'm concerned about what this means. Is it contaminated? Is it degraded? Is it still safe to use? I've used Ozempic pens before, and they were always clear. This is different from my usual pens. I called my doctor and they said not to use it and to get a replacement. I'm going to return it to the pharmacy. But I wanted to report this because this is a quality concern. If the solution looks different, that suggests something might be wrong with it. It could be contamination, or it could be that the medication has degraded. Either way, it's a quality issue that needs to be addressed. I'm documenting this as a product complaint because the abnormal appearance suggests potential contamination or degradation.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports abnormal product appearance suggesting contamination or degradation, identified before use.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. So when I dial the dose, the pen makes a grinding noise. Like, a really loud grinding or scraping sound. It doesn't sound right at all. My previous pens made a smooth clicking sound, but this one sounds broken. I'm worried that if it sounds broken, maybe it won't deliver the right amount of medication. What if the mechanism is damaged and I'm not getting the correct dose? I just opened this pen, it's brand new. I haven't used it yet because I'm concerned about the noise. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a quality issue. The pen should operate smoothly and quietly. If it's making grinding noises, that suggests the mechanism is damaged or defective. This could affect dosing accuracy. I'm documenting this as a product complaint because the abnormal operation suggests a mechanical defect.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes abnormal device operation suggesting mechanical defect, a quality issue affecting confidence in dosing.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I got my Ozempic pen, and when I opened the box, I noticed that the needles inside are the wrong size. The box contains 8 millimeter needles, but I was prescribed 4 millimeter needles. My doctor specifically prescribed 4 millimeter needles because I'm thin and have less subcutaneous tissue. The 8 millimeter needles are too long for me - they could hit muscle or cause more pain. I can't use these needles safely. I called my pharmacy and they said this is a packaging error - the wrong needles were included in the box. They're going to send me the correct needles, but I wanted to report this because this is a quality control issue. If people get the wrong needle size, they might not be able to use the medication safely, or they might use the wrong size and have problems. This is a product configuration error that affects usability and safety. I'm documenting this as a product complaint because it's an incorrect component packaging issue.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports incorrect component packaging, a dispensing or product configuration error without patient harm.",
        },
    ]

    return training_data


def generate_test_data():
    """Generate test examples for evaluation."""

    test_data = [
        # Adverse Events (10 examples)
        {
            "complaint": add_transcription_artifacts(
                """So I've been on Ozempic for about six months now, and I've been doing really well with my blood sugar and weight loss. I've lost about forty pounds, which is great. But about a month ago, I started having this really bad pain in my right upper abdomen. Like, really sharp pain, especially after I eat. It got worse and worse, and finally I went to my doctor. They did an ultrasound and found gallstones. The doctor said I have cholelithiasis, and the stones are pretty large. I ended up needing surgery to remove my gallbladder. The surgeon said that rapid weight loss can cause gallstones, and since I've lost forty pounds in six months on the Ozempic, that's probably what caused it. So it's not directly the medication, but the weight loss from the medication led to the gallstones. I'm doing okay after the surgery, but it was scary. I had to have laparoscopic surgery, which wasn't too bad, but still. I'm documenting this because even though it's indirect, the medication's effect caused a serious problem that required surgery.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious adverse event (cholelithiasis) requiring surgical intervention, indirectly caused by medication-induced rapid weight loss.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about my patient who had a serious complication. So the patient has been on Ozempic for about three months, and they've been having a lot of GI side effects - nausea, vomiting, diarrhea. It's been pretty bad, but manageable. Last week, the patient was vomiting really severely, and they aspirated some of the vomit into their lungs. They ended up with aspiration pneumonia. They were hospitalized for five days on IV antibiotics. The patient also has GERD, which they've had for years, so that was a contributing factor. But the severe vomiting from the Ozempic definitely made the aspiration more likely. The patient is doing better now, but it was a serious infection. I'm documenting this as an adverse event because the medication's side effects led to a serious complication requiring hospitalization. Even though there were other factors, the Ozempic's GI effects were a major contributor.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes serious complication (aspiration pneumonia) resulting from GI adverse effects of Ozempic, even with contributing factors.",
        },
        {
            "complaint": add_transcription_artifacts(
                """Hi, um, I need to report something that's been happening. So I started Ozempic about two months ago, and I've been having these episodes where my heart starts racing. Like, really fast, up to 120 beats per minute even when I'm just sitting down. It feels like my heart is going to beat out of my chest. I went to my cardiologist and he did an EKG and found that I'm having episodes of atrial fibrillation. I've never had any heart problems before, no family history, nothing. The timing is suspicious because it started about a month after I began Ozempic. But I'm also under a lot of stress at work, and I've been drinking more coffee lately. So I don't know if it's the medication or something else. My cardiologist said it could be related to the Ozempic, but he's not 100% sure. He started me on a beta blocker, which helps some, but I'm still having episodes. I'm documenting this because even though we're not certain, the timing suggests it could be related to the medication.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports cardiac adverse event (new atrial fibrillation) temporally related to Ozempic initiation, despite other potential contributing factors.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This is really concerning. So I've been injecting Ozempic for about four months now, and I've been doing the injections in my abdomen, rotating sites. About two weeks ago, I noticed one of my injection sites was really red and swollen, and it was getting worse. It became really painful, and it started draining pus. I went to urgent care, and the doctor said it was an abscess. They had to do an incision and drainage procedure right there. It was really painful. They sent a culture, and it came back positive for staph aureus. I had to take antibiotics for two weeks. The doctor asked me about my injection technique, and I've been following all the instructions - cleaning the site, using a new needle every time, everything. This has never happened with any other medication I've injected. I'm really worried about injecting again because I don't want another infection. The doctor said this could be from contamination or improper technique, but I've been really careful. I think this is related to the Ozempic injections somehow.""",
                0.4,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes serious infection at injection site requiring surgical intervention, an adverse event from drug administration.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about something that's really upsetting me. So I've been on Ozempic for about three months, and I've lost about twenty-five pounds, which is great. But about a month ago, I started noticing that my hair was falling out. Like, a lot. I'm losing handfuls of hair in the shower, it's coming out when I brush it, it's everywhere. I went to my doctor and she said it's telogen effluvium, which is hair loss that can happen after stress or major changes to your body. She thinks it's related to the rapid weight loss from the Ozempic. So it's not directly from the medication itself, but from the weight loss the medication causes. I'm really upset because I'm losing my hair, and it's affecting my self-esteem. I don't know if I should stop the medication, but my blood sugar is so much better. This is really affecting my quality of life. I think this needs to be documented because even though it's indirect, it's a significant problem.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports adverse effect (alopecia) indirectly related to medication-induced rapid weight loss, affecting patient quality of life.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So this is kind of complicated. My patient has been on Ozempic for about four months, and he's been having really bad constipation. Like, really severe. He's been taking laxatives, but they're not helping much. Last week, he came into the ER with severe abdominal pain and distension. We did a CT scan and found a partial bowel obstruction. He was admitted for three days, had to have an NG tube, IV fluids, the whole thing. Now, constipation is a known side effect of Ozempic, and severe constipation can lead to bowel obstruction. But the patient also has a history of diverticulosis, which can predispose to obstruction. So it's not entirely clear if this is directly from the Ozempic or if the Ozempic just made an underlying condition worse. But the timing is suspicious, and the constipation from Ozempic definitely contributed. I'm documenting this as an adverse event because the medication's side effect led to a serious complication requiring hospitalization.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious GI complication (bowel obstruction) requiring hospitalization, potentially related to Ozempic-induced constipation.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about my patient who had a serious reaction. So the patient started Ozempic about three weeks ago, and after the second dose, they developed a rash all over their body. Like, everywhere - arms, legs, trunk, everywhere. They also had a fever of 102 degrees Fahrenheit. They came into my office, and I sent them for labs. Their liver enzymes were elevated - ALT was 180, AST was 150, which is significantly elevated. Normal is under 40. This looks like a systemic hypersensitivity reaction with organ involvement. The patient had no history of liver disease, no other medications that could cause this. The timing is very suspicious - second dose of Ozempic, and then this reaction. I stopped the medication immediately and started them on steroids. The rash is improving, but the liver enzymes are still elevated. This is a serious adverse drug reaction. I'm documenting this as an adverse event because it's a systemic hypersensitivity reaction with organ involvement, which is serious.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes systemic hypersensitivity reaction with organ involvement, a serious adverse drug reaction.",
        },
        {
            "complaint": add_transcription_artifacts(
                """Hi, um, I need to report something that's been happening since I started Ozempic. So I started Ozempic 1 milligram about six weeks ago, and I've been feeling really anxious and jittery. Like, really anxious, all the time. My heart races, I can't sleep, I feel like I'm on edge constantly. I've never had anxiety before this medication. I've always been a pretty calm person. But since starting Ozempic, I've been having panic attacks. My doctor said this could be related to the medication, but it's not a common side effect. I'm not sure if I should continue taking it, but my blood sugar is so much better. This is really affecting my quality of life though. I'm having trouble sleeping, I'm irritable, I'm not myself. I think this needs to be documented because it's a significant problem that started after I began the medication.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports new onset psychiatric and autonomic symptoms temporally related to starting Ozempic.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a serious problem. So my patient has been on Ozempic for about four months, and they're also on a statin for cholesterol. About two weeks ago, they came in complaining of severe muscle pain and weakness. Like, really severe - they could barely walk. I sent them for labs, and their creatine kinase level was 8000. Normal is under 200. That's extremely elevated. They were diagnosed with rhabdomyolysis, which is a serious condition where muscle breaks down. This could be from the statin, or it could be from an interaction between the statin and Ozempic, or it could be from the Ozempic itself. We stopped both medications immediately. The patient is doing better now, but it was serious. They had to be monitored closely for kidney damage. I'm documenting this as an adverse event because it's a serious condition that could be related to the medication or a drug interaction.""",
                0.25,
            ),
            "label": "Adverse Event",
            "reasoning": "Reports serious adverse event (rhabdomyolysis) with lab confirmation, potentially related to drug interaction.",
        },
        {
            "complaint": add_transcription_artifacts(
                """This was really scary. So I've been on Ozempic for about five weeks, and I've been having a lot of nausea and vomiting. It's been pretty bad, but I was trying to stick with it because my doctor said the side effects should improve. But last week, I was vomiting really badly for two weeks straight. I couldn't keep anything down, not even water. I got really dehydrated. My blood pressure dropped really low, and I actually passed out. My husband found me on the floor and called 911. The paramedics came and took me to the hospital. I was really dehydrated, my blood pressure was 80 over 50, which is dangerously low. They gave me IV fluids and kept me overnight. The doctors said the vomiting from Ozempic caused severe dehydration, which led to low blood pressure and fainting. I'm better now, but it was really scary. I've stopped the medication because I can't deal with this level of side effects. I think this needs to be reported because it was a serious complication.""",
                0.4,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes serious complications (dehydration, hypotension, syncope) from medication adverse effects requiring emergency care.",
        },
        # Product Complaints (10 examples)
        {
            "complaint": add_transcription_artifacts(
                """Hi, I need to report a problem with my Ozempic pen. So I got a new pen last week, and when I tried to use it, it clicks when I dial the dose, but when I press the injection button, no medication comes out. Like, nothing. I've tried it three times now, same thing every time. I can hear it clicking when I dial, and the counter shows the dose, but when I press the button to inject, nothing happens. I've used Ozempic pens before, so I know how to use them. I'm following all the steps correctly. The pen seems defective - like there's something wrong with the internal mechanism that delivers the medication. I haven't had any adverse effects because I haven't actually gotten any medication from it, but I'm missing doses which isn't good for my diabetes. I called my pharmacy and they said I need to report this to the manufacturer. This is definitely a product defect.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports mechanical malfunction preventing medication delivery, a device defect without reported patient harm.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. So the label on the pen is peeling off. Like, it's coming off in strips, and I can't read the lot number or expiration date anymore. The label is all smudged and unreadable. I'm really concerned because I need to know when this pen expires, and I need the lot number in case there's a recall or something. I called my pharmacy and they said this is a quality control issue. They're going to send me a replacement, but I wanted to report this because this is a labeling defect. If people can't read the label, they might not know important information about the product. This is a quality issue that needs to be addressed.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes labeling defect affecting product identification and traceability, a quality issue.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I received my Ozempic pen in the mail, and when I opened the shipping box, the pen was frozen solid. Like, completely frozen. It was supposed to be shipped with ice packs to keep it cold, but it was frozen, not just cold. The pen was hard as a rock. I called my pharmacy and they said the medication is probably ruined now. Ozempic is supposed to be refrigerated, not frozen. If it freezes, it can damage the medication and make it ineffective. I'm really frustrated because I've wasted a pen, and these are expensive. I haven't used it because I don't know if it's still good, and I don't want to risk using ineffective medication. This is a cold chain failure - the product wasn't stored or shipped at the correct temperature. I'm documenting this as a product complaint because it's a storage and shipping issue that affects product quality.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports cold chain failure with product freezing, affecting medication potency and quality.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about something I noticed when I opened my Ozempic pen box. So I got a new pen yesterday, and when I opened the box, the protective seal on the pen was already broken. Like, it was torn and partially detached. The package also looked like it might have been previously opened - the outer box had some damage, and the inner packaging looked tampered with. I'm really concerned about contamination. If the seal is broken, the pen might not be sterile anymore. I haven't used it because I'm worried about infection or contamination. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a packaging integrity issue. If the packaging is compromised, the product could be contaminated or tampered with. This is a quality and safety concern.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes compromised packaging integrity raising sterility concerns, a product tampering or quality issue.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So this is confusing. I got my Ozempic pen, and when I looked at it, the box says 0.5 milligrams, but the pen itself is labeled 1.0 milligrams. There's a mismatch between the box label and the pen label. I don't know which one is correct. I called my pharmacy and they said they dispensed 0.5 milligrams, so that's what should be in there. But the pen says 1.0 milligrams. I'm really confused and concerned. What if I use it and get the wrong dose? That could be dangerous. I haven't used it yet - I'm waiting to hear back from my doctor about what to do. But I wanted to report this because this is a labeling error. It could be a pharmacy dispensing error, or it could be a manufacturing labeling problem. Either way, it's a product identification issue that could affect patient safety.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports labeling mismatch or dispensing error, a product identification issue without patient use or harm.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. So the injection button is completely stuck. Like, I can't depress it at all, no matter how hard I push. I've tried everything - pushing it straight down, twisting it, nothing works. It's like it's frozen in place. I can dial the dose fine, the counter works, but I can't actually inject because the button won't move. This is a brand new pen, I just opened it. I'm completely unable to use it. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a mechanical failure. If the button doesn't work, people can't use the pen at all. This is a product defect that prevents use of the medication. I'm documenting this as a product complaint because it's a device malfunction.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes device mechanical failure preventing use, a product defect without adverse patient reaction.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I got my Ozempic pen, and when I looked at the solution inside, it looks cloudy instead of clear. Like, it's not transparent like it should be. It looks milky or hazy. I haven't used it yet because I'm concerned about what this means. Is it contaminated? Is it degraded? Is it still safe to use? I've used Ozempic pens before, and they were always clear. This is different from my usual pens. I called my doctor and they said not to use it and to get a replacement. I'm going to return it to the pharmacy. But I wanted to report this because this is a quality concern. If the solution looks different, that suggests something might be wrong with it. It could be contamination, or it could be that the medication has degraded. Either way, it's a quality issue that needs to be addressed.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports abnormal product appearance suggesting contamination or degradation, identified before use.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem with my Ozempic pen. So when I dial the dose, the pen makes a really loud grinding noise. Like, a grinding or scraping sound. It doesn't sound right at all. My previous pens made a smooth clicking sound, but this one sounds broken. I'm worried that if it sounds broken, maybe it won't deliver the right amount of medication. What if the mechanism is damaged and I'm not getting the correct dose? I just opened this pen, it's brand new. I haven't used it yet because I'm concerned about the noise and what it might mean for dosing accuracy. I called my pharmacy and they're sending me a replacement, but I wanted to report this because this is a quality issue. The pen should operate smoothly and quietly. If it's making grinding noises, that suggests the mechanism is damaged or defective.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes abnormal device operation suggesting mechanical defect, a quality issue affecting confidence in dosing.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So I got my Ozempic pen, and when I opened the box, I noticed that the needles inside are the wrong size. The box contains 8 millimeter needles, but I was prescribed 4 millimeter needles. My doctor specifically prescribed 4 millimeter needles because I'm thin and have less subcutaneous tissue. The 8 millimeter needles are too long for me - they could hit muscle or cause more pain. I can't use these needles safely. I called my pharmacy and they said this is a packaging error - the wrong needles were included in the box. They're going to send me the correct needles, but I wanted to report this because this is a quality control issue. If people get the wrong needle size, they might not be able to use the medication safely, or they might use the wrong size and have problems. This is a product configuration error.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Reports incorrect component packaging, a dispensing or product configuration error without patient harm.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a major error I found. So I got my Ozempic pen, and when I opened the box, I looked at the user manual that came with it. But the manual is for a completely different product - it's for Victoza, which is also made by Novo Nordisk, but it's a different medication. The instructions are completely wrong. They're talking about a different pen, different dosing, everything is wrong. This is a serious packaging error. If someone uses the wrong instructions, they could use the pen incorrectly, which could be dangerous. I called my pharmacy and they're sending me the correct manual, but I wanted to report this because this is a major error. The product should have the correct instructions. This is a regulatory compliance issue - the wrong instructions could lead to medication errors.""",
                0.25,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes serious labeling/packaging error with incorrect product instructions, a regulatory compliance issue.",
        },
        # Nuanced/Edge Cases - Test Set (5 examples)
        {
            "complaint": add_transcription_artifacts(
                """So this is a complicated situation. I've been on Ozempic for about three months, and I've been having some issues, but I'm not sure if it's an adverse event or a product problem. So I've been having a lot of injection site reactions - redness, swelling, pain. But here's the thing - it only happens with some pens, not all of them. Like, I'll get a new pen, and some pens cause reactions and some don't. I've been using the same injection technique, same site preparation, everything. But some pens cause really bad reactions and some don't. I'm wondering if there's something wrong with specific pens - like, maybe some pens have a different pH or something that's causing the reactions? Or maybe it's just an adverse reaction that happens sometimes? I'm really confused. My doctor said it could be either - it could be an adverse reaction to the medication, or it could be a product quality issue with specific pens. I'm documenting this because I think it's important, but I'm not sure which category it falls into.""",
                0.35,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes injection site reactions that occur inconsistently - likely adverse event rather than product defect since patient follows consistent technique.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about something that happened, but I'm not sure if it's really a problem or not. So I've been on Ozempic for about two months, and I've been having some GI side effects - nausea, some diarrhea. But it's been manageable. Last week, I noticed that my pen was leaking a little bit after I injected. Like, a small amount of medication would leak out around the needle site after I removed the needle. I'm not sure if this is normal or if it's a problem with the pen. I'm worried that I'm not getting the full dose because some medication is leaking out. But I'm also having GI side effects, which suggests I am getting medication. I don't know if the leaking is a product defect or if it's just normal, or if it's related to my injection technique. I called my pharmacy and they said to report it, but I'm not sure if this is a product complaint or if it's just how the pen works. I'm documenting this because I'm concerned about getting the correct dose.""",
                0.3,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes medication leakage after injection - product defect affecting dose delivery, even if some medication is being delivered.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So this is kind of a gray area. I've been on Ozempic for about four months, and I've been doing really well. But about a month ago, I started having these episodes where I feel really weak and dizzy, and my blood sugar drops. But here's the thing - I'm not sure if it's the medication causing hypoglycemia, or if it's because I'm eating less because of the nausea from the medication. Like, is it a direct effect of the medication lowering my blood sugar, or is it an indirect effect because the medication makes me nauseous so I eat less? I've had to go to the ER twice because my blood sugar got really low. The doctors said it could be either - it could be the medication directly affecting blood sugar, or it could be from not eating enough because of the side effects. I'm documenting this because it's a serious problem, but I'm not entirely sure of the mechanism.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes hypoglycemic episodes - adverse event whether directly from medication or indirectly from medication-induced reduced food intake.",
        },
        {
            "complaint": add_transcription_artifacts(
                """I'm calling about a problem I've been having. So I've been on Ozempic for about three months, and I've been having issues with the pens. Like, sometimes the dose counter doesn't reset properly after I inject. It stays on the dose I just injected instead of going back to zero. This happens with some pens but not others. I'm worried that if the counter doesn't reset, I might accidentally inject the same dose twice, or I might not know how much medication is left in the pen. I've called my pharmacy and they said this could be a product defect, but they're not sure. They're sending me replacement pens. But I'm also concerned that if I do accidentally inject twice, that could cause an overdose, which would be an adverse event. So I'm not sure if this is a product complaint or if it could lead to an adverse event. I'm documenting this because it's a safety concern.""",
                0.35,
            ),
            "label": "Product Complaint",
            "reasoning": "Describes dose counter malfunction - product defect that could potentially lead to dosing errors, but no adverse event has occurred yet.",
        },
        {
            "complaint": add_transcription_artifacts(
                """So this is complicated. I've been on Ozempic for about five months, and I've been having some problems, but I'm not sure what's causing them. I've been having a lot of fatigue and weakness, and I've been losing weight, but not in a good way - I'm losing muscle mass, not just fat. I went to my doctor and they did labs, and my protein levels are low, which suggests malnutrition. But I'm not sure if this is from the Ozempic causing malabsorption, or if it's because I'm eating less because of the nausea, or if it's something else entirely. The doctor said it could be related to the medication, but it's not clear. I'm documenting this because it's a serious problem, but I'm not entirely sure if it's an adverse event from the medication or if it's something else. The timing is suspicious though - it started after I began Ozempic.""",
                0.3,
            ),
            "label": "Adverse Event",
            "reasoning": "Describes malnutrition and muscle loss - adverse event likely related to medication effects on nutrition, whether direct or indirect.",
        },
    ]

    return test_data


def write_datasets(train_path: Path = TRAIN_FILE, test_path: Path = TEST_FILE) -> None:
    """Write the synthetic datasets to disk."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with train_path.open("w", encoding="utf-8") as train_fp:
        json.dump(generate_training_data(), train_fp, indent=2, ensure_ascii=False)

    with test_path.open("w", encoding="utf-8") as test_fp:
        json.dump(generate_test_data(), test_fp, indent=2, ensure_ascii=False)

    print(f"✓ Wrote training data to {train_path}")
    print(f"✓ Wrote test data to {test_path}")


def main():
    write_datasets()


if __name__ == "__main__":
    main()
