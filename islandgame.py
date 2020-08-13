# imports from other libraries
import os, sys
import random
from PyQt5.QtWidgets import QApplication

# imports from intficpy
from intficpy.daemons import Daemon
from intficpy.grammar import GrammarObject
from intficpy.ifp_game import IFPGame
from intficpy.room import Room, OutdoorRoom, RoomGroup
from intficpy.things import Thing, Surface, Container, Clothing, Abstract, Key, Lock, UnderSpace, LightSource, Transparent, Readable, Book, Pressable, Liquid
from intficpy.score import Achievement, Ending, HintNode, Hint, hints, score
from intficpy.travel import TravelConnector, DoorConnector, LadderConnector, StaircaseConnector
from intficpy.actor import Actor, Player, Topic, SpecialTopic
from intficpy.verb import Verb
import intficpy.gui as gui

# Translate asset paths to useable format for PyInstaller
def resource_path(relative_path):
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath('.'), relative_path)

app = QApplication(sys.argv)
ex = gui.App()

# HACK: instances are actually tracked on the IFPObject subclass
rooms = {key: value for key, value in Room.instances.items() if isinstance(value, Room)}

storm_turns_left = 30
storm_turns_full = 30

def skyState():
	if	storm_turns_left==storm_turns_full:
		return "The sky is clear today. "
	else:
		return "The sky is dark, and stormy. "

# rooms
# SHACK 0
shack0 = Room("Shack interior", "You are in wooden shack. Light filters in through a cracked, dirty window. ")
shack0.storm_desc = "You are in wooden shack. Lightning flashes in the cracked window. The walls creak from the storm winds. "
me = Player("me")

game = IFPGame(me, ex)
game.aboutGame.title = "ISLAND IN THE STORM"
game.aboutGame.author = "JSMaika"
game.aboutGame.game_instructions = "<i>Island in the Storm</i> is a fantasy puzzle game with mystery elements. The objective of the game is to escape the island. In order to do this, you will need to explore, solve puzzles and interact with islanders. A few hints:<br><br>While the game accepts conversation commands in the classic interactive fiction ask/tell/give/show format, all conversation topics can be reached through TALK TO. To talk about the suggested topics (listed in parentheses under the character's response), type out all or part of the suggestion. For instance, you could accept the suggestion, \"You could ask what the woman does for a living,\" by typing ASK WHAT THE WOMAN DOES FOR A LIVING. Unless there were other suggestions that used the word \"living\", you could also just type LIVING. Suggestions are only available immediately after they are given. <br><br>When travelling through dark areas, bring your light crystal. It recharges in full light. At full charge, it will last 50 turns. Be sure not to let it die while you're in the dark.<br><br>This game is not hint enabled. In the event that you get stuck, you can consult the walkthrough, which should have been included with your distribution package. Look for island-walkthrough.txt<br><br>Good luck!"
game.aboutGame.betaTesterCredit = "Thank you to beta testers <br>Michael Csokas, <br>Rosa,<br> and Shaun"

def killMyself(game):
	game.addText("Oh, come now. Don't give up just yet. ")
me.killVerbDobj = killMyself

bed0 = Surface("bed")
bed0.describeThing("There is a bed here. ")
bed0.xdescribeThing("There is a bed here. {bedBoxDesc(game)}")
def bedBoxDesc(game):
	if underbed0.containsItem(opalbox):
		return "It looks like there might be something underneath. "
bed0.canLie = True
shack0.addThing(bed0)
#shack0.addThing(me)
bed0.addThing(me)
me.setPlayer()
me.position = "lying"
underbed0 = UnderSpace("bed")
underbed0.contains_preposition = "under"
bed0.addComposite(underbed0)

# ABSTRACTS
#goddess_abs = Abstract("goddess")
goddess_abs = Actor("goddess")
goddess_abs.describeThing("")
goddess_abs.level = 0
goddess_abs.cannot_interact_msg = "The Goddess of the Storm isn't a physical being you can interact with. "

def buyGoddess(game, iobj):
	game.addText("That is impossible. ")
goddess_abs.buyFromVerbDobj = buyGoddess

def breakGoddess(game):
	game.addText("The Goddess of the Storm is unbreakable. ")
goddess_abs.breakVerbDobj = breakGoddess

def killGoddess(game):
	game.addText("Hah! It's not going to be <i>that</i> easy. ")
goddess_abs.killVerbDobj = killGoddess

def giveGoddess(game, iobj):
	if iobj is me:
		game.addText("You kneel before the Goddess of the Storm, and offer your soul to Her. You feel Her claws closing around you.<br><br><i>YES, CHILD. COME TO ME. REST.</i><br><br>You feel a calm settling over you - peace, like nothing you've ever felt. It is beautiful. The Goddess of the Storm is beautiful, with her silver scales, and many eyes. You are Hers now, and you are glad. ")
		global special_box_style
		
		kaur_ending.endGame(game)
	else:
		game.addText("Nothing happens. ")
goddess_abs.giveVerbDobj = giveGoddess

def getGoddessDesc():
	if goddess_abs.level == 1:
		return "<i>Examine</i> the Goddess of the Storm? What would that even mean?"
	elif goddess_abs.level == 2:
		return "You don't see the Goddess, but you can feel <i>something</i>. You've been feeling a strange presence for a while now. "
	elif goddess_abs.level == 2 and me.getOutermostRoom.room_group == cave_group:
		return "You can still feel the Goddess of the Storm, but her presence is much weaker here in the caves. "
	elif goddess_abs.level == 3:
		return "The Goddess of the Storm rages through the sky above you. You need to move quickly."
	else:
		return "You can't see anything like that around here. "
goddess_abs.describeThing("")
goddess_abs.ignore_if_ambiguous = True
goddess_abs.xdescribeThing(f"{getGoddessDesc()}")
goddess_abs.cannotTakeMsg = "That is impossible. "
goddess_abs.addSynonym("storm")
goddess_abs.setAdjectives(["goddess", "of"])
goddess_abs._verbose_name = "Goddess of the Storm"
goddess_abs.isDefinite = True
previous_no_offering = False
previous_kaur_offering = False
previous_bad_offering = False

def prayerAnswered(game):
	game.daemons.add(goddessStormDaemon)
	square21.removeThing(villagers21)
	square21.removeThing(woman21)
	square21.removeThing(children21)
	square21.removeThing(man21)
	goddess_abs.level = 3
	lightcrystal.location.removeThing(lightcrystal)
	game.daemons.remove(crystalCharge)
	kaur_cup.location.removeThing(kaur_cup)
	disk.location.removeThing(disk)
	fan.location.removeThing(fan)
	for key, item in Thing.instances.items():
		storm_desc = getattr(item, "storm_desc", None)
		if isinstance(item, Room):
			try:
				item.desc = item.storm_desc
			except AttributeError:
				pass
			continue
		if isinstance(item, Actor):
			try:
				item.setHermitTopic(item.storm_hermit_state)
			except AttributeError:
				pass
		if isinstance(item, Thing):
			try:
				item.describeThing(item.storm_desc)
			except AttributeError:
				pass
			try:
				item.xdescribeThing(item.storm_xdesc)
			except AttributeError:
				pass

	game.addText("<i>I SEE. YOU WISH ME TO SET MY CHILDREN FREE? THEN FREE THEY SHALL BE. FREE FROM MY CARE. FREE FROM MY PROTECTION. AND WHAT I DO NOT PROTECT, I DESTROY. </i>")
	game.addText("The sky darkens. Rain starts to fall. Within moments, a storm has begun. ")
	game.addText("<i>THIS IS THE END, HUMAN. </i>")
	global special_box_style
	
	offeringAchievement.award(game)

prayer_topic1 = SpecialTopic("whisper the prayer from the cavern wall", "You whisper the prayer from the cavern wall.  <br><br><i>You who brings the rain, I pray thee, listen. <br>You who protects this land, <br>You who kills the interloper; sinks ships; holds our hearts - <br>Hear my cry, O Goddess of the Storm, <br>Come before me now, <br>See my flesh and soul, <br>Take the gifts I offer. Hear my request. <br>So be it.</i>")
#goddess_abs.addSpecialTopic(prayer_topic1)
def prayerTopic1(app, suggest=True):
	global previous_no_offering
	global previous_kaur_offering
	global previous_bad_offering
	global special_box_style
	game.addText(prayer_topic1.text)
	loc = me.getOutermostLocation()
	if loc == temple29:
		if altar_n29.contains == {} and altar_s29.contains == {} and altar_e29.contains == {} and altar_w29.contains == {}:
			if not previous_no_offering:
				game.addText("The Goddess' presence intensifies. A voice whispers in your mind, faint but sharp; angry. <br><br><i>You stand in my temple and demand my attention while you offer me nothing? Do not try my patience further, Outsider. </i>")
				previous_no_offering = True
			else:
				game.addText("The Goddess' presence intensifies. A voice roars in your mind, like the crashing of waves. <br><br><i>YOU ARE AN OUTSIDER. YOU ARE AN ENEMY. I HAVE OFFERED YOU MY GIFT, AND YOU HAVE TURNED ME DOWN. AGAIN, YOU CRY OUT TO ME LIKE A MEWLING KITTEN. AGAIN, YOU OFFER ME NOTHING. HERE IS MY ANSWER, FOOL: DIE WHERE YOU STAND. </i>")
				
				insult_goddess_ending.endGame(game)
		elif altar_n29.containsItem(kaur_liquid) or altar_s29.containsItem(kaur_liquid) or altar_e29.containsItem(kaur_liquid) or altar_w29.containsItem(kaur_liquid):
			if not previous_kaur_offering:
				
				game.addText("The Goddess' presence intensifies. A voice hisses in your mind, an angry warning. <br><br><i>Do not offer me Kaur when you will not drink it, outsider.</i>")
				previous_kaur_offering = True
			else:
				
				game.addText("The Goddess' presence intensifies. A voice roars in your mind, like the crashing of waves. <br><br><i>I HAVE GIVEN YOU THE CHANCE TO ASSIMILATE, OUTSIDER. I HAVE BEEN PATIENT. I HAVE SENT MY CHILDREN TO YOU IN FRIENDSHIP. NOW, STILL FOREIGN, STILL OTHER, STILL ENEMY, YOU CLAIM THE RIGHT OF MY DEVOTED? I HAVE WARNED YOU ONCE, YET YOU STILL DEFY ME. LET THIS BE YOUR LAST MISTAKE. </i>")
				
				insult_goddess_ending.endGame(game)
		else:
			correct = 0
			incorrect = 0
			# WEST: OCEAN
			if seawater_taken.ix in altar_w29.sub_contains and len(altar_w29.contains)==1:
				correct += 1
			elif altar_w29.contains != {}:
				incorrect += 1
			# NORTH: DISK OF EARTH
			if altar_n29.containsItem(disk) and len(altar_n29.contains)==1:
				correct += 1
			elif altar_n29.contains != {}:
				incorrect += 1
			# SOUTH: POWER OF THE SUN
			if altar_s29.containsItem(lightcrystal) and len(altar_s29.contains)==1:
				correct += 1
			elif altar_s29.contains != {}:
				incorrect += 1
			# EAST: WING
			if altar_e29.containsItem(fan) and len(altar_e29.contains)==1:
				correct += 1
			elif altar_e29.contains != {}:
				incorrect += 1
			if incorrect == 0 and correct ==1:
				
				game.addText("The Goddess' presence intensifies. A voice whispers in your mind, faint, and mocking. <br><br><i>One offering? It will take more than that, Outsider. </i>")
			elif incorrect == 0 and correct ==2:
				
				game.addText("The Goddess' presence intensifies. A voice whispers in your mind, quiet, but rough. <br><br><i>You have caught my attention, Mortal. Perhaps you are less foolish than you seem. </i>")
			elif incorrect == 0 and correct ==3:
				
				game.addText("The Goddess' presence intensifies. You feel her watching you intently. A voice whispers in your mind. <br><br><i>I am waiting for the fourth, Outsider. </i>")
			elif incorrect == 0 and correct ==4:
				
				game.addText("The Goddess' presence intensifies. A voice roars in your mind, like the crashing of waves. <br><br><i>YOU HAVE PLACED BEFORE ME THE DISK, THE WING, THE SUN, THE OCEAN. I AM HERE. I AM LISTENING. WHY DID YOU CALL FOR ME? </i>")
				prayerAnswered(game)
			elif not previous_bad_offering:
				
				game.addText("The Goddess' presence intensifies. A voice whispers in your mind, faint, and mocking. <br><br><i>This is what you offer? Pathetic. Give me a real offering, and perhaps I shall answer your prayer. </i>")
				previous_bad_offering = True
			else:
				game.addText("Nothing happens. Maybe you should offer something else. ")
	else:
		game.addText("Nothing happens. Maybe you should try praying at the temple. ")
prayer_topic1.func = prayerTopic1
# storm abstract, which is replaced as a concept by the goddess once the player learns of her
storm_abs = Abstract("storm")
storm_abs.setAdjectives(["wind"])
storm_abs._verbose_name = "storm"
storm_abs.isDefinite = True

storm_abs.makeKnown(me)

# THINGS USED IN CUSTOM
# configured with starting rooms
rock_barriers = []
shore8 = OutdoorRoom("Shore, Site of a Half-Buried Wreck", "There is a short patch of sand along the shore. ")
shore8.ceiling.xdescribeThing(skyState())
lightcrystal = LightSource("crystal")
lightcrystal.addSynonym("light")
lightcrystal.setAdjectives(["light"])
lightcrystal.consumable = True
lightcrystal.turns_left = 5
lightcrystal.max_turns = 50 #15?
lightcrystal.player_can_light = False
lightcrystal.player_can_extinguish = False
lightcrystal.cannot_light_msg = "Once charged by sunlight, the crystal will light itself in darkness. "
lightcrystal.cannot_extinguish_msg = "The crystal cannot be put out, except by placing it in the light. "
def _consumeLightCrystalDaemon(game):
	from intficpy.verb import helpVerb, helpVerbVerb, aboutVerb
	if not (game.parser.previous_command.verb==helpVerb or game.parser.previous_command.verb==helpVerbVerb or game.parser.previous_command.verb==aboutVerb or game.parser.previous_command.ambiguous or game.parser.previous_command.err):
		lightcrystal.turns_left  -= 1
		if lightcrystal.turns_left == 0:
			if me.getOutermostLocation() == lightcrystal.getOutermostLocation():
				game.addText(lightcrystal.extinguishing_expired_msg)
			lightcrystal.is_lit = False
			if lightcrystal.consumeLightSourceDaemon in game.daemons.active:
				game.daemons.remove(lightcrystal.consumeLightSourceDaemon)
		elif me.getOutermostLocation() == lightcrystal.getOutermostLocation():
			global special_box_style
			if lightcrystal.turns_left < 5:
				game.addText(lightcrystal.expiry_warning + str(lightcrystal.turns_left) + " turns left. ")
			elif (lightcrystal.turns_left % 5)==0:
				game.addText(lightcrystal.expiry_warning + str(lightcrystal.turns_left) + " turns left. ")
consumeLightCrystalDaemon = Daemon(_consumeLightCrystalDaemon)
lightcrystal.consumeLightSourceDaemon = consumeLightCrystalDaemon
boat_sail = Thing("sail")
boat_power = Thing("crystal")
myboat = Container("boat")
needlethread = Thing("thread")
needlethread.addSynonym("needle")
needlethread.addSynonym("notions")
needlethread.setAdjectives(["needle", "and", "spool", "of", "sewing"])
needlethread._verbose_name = "needle and thread"
needlethread.xdescribeThing("The needle has been threaded, and tucked into the spool. ")
needlethread.describeThing("There is a needle and thread here. ")
patchkit = Thing("kit")
patchkit.addSynonym("patch")
patchkit.setAdjectives(["patch"])
patchkit.describeThing("There is a patch kit here. ")
patchkit.xdescribeThing("The patch kit contains everything you will need to repair your hull. ")
def usePatchkit(game):
	if me.getOutermostLocation()==shore6:
		repairWithVerb.verbFunc(game, myboat, patchkit)
	else:
		game.addText("There's nothing here that needs to be patched. ")
	return False
patchkit.useVerbDobj = usePatchkit

shovel = Thing("shovel")
def useShovel(game):
	digWithVerb.verbFunc(game, shovel)
	return False
shovel.useVerbDobj = useShovel

shovel.xdescribeThing("The shovel is metal, with a wooden handle. ")
compass = Thing("compass")
compass.setAdjectives(["rusty"])
compass.xdescribeThing("The casing of this compass is a little rusty, but it still functions perfectly. ")
mycompass = Abstract("compass")
mycompass.setAdjectives(["my", "your"])
mycompass._verbose_name = "your compass"
mycompass.has_proper_name = True
lens = Transparent("lens")
lens.setAdjectives(["arais", "enchanted"])
lens.has_proper_name = True
lens._verbose_name = "Arai's enchanted lens"
lens.describeThing("Arai's enchanted lens is here. ")
lens.size = 15
lens.xdescribeThing("The lens is about the size of your palm, and faintly violet tinted. According to Arai, looking through it will reveal things that have been magically concealed. ")
pickaxe = Thing("pickaxe")
pickaxe.xdescribeThing("The pickaxe is metal, with a wooden handle. ")
pickaxe.size = 40
kaur_cup = Container("cup")
kaur_cup.size = 25
kaur_cup.holds_liquid = True
kaur_cup.setAdjectives(["white", "ceramic"])
kaur_liquid = Liquid("Kaur", "kaur")
kaur_liquid.addSynonym("kaur")
kaur_liquid._verbose_name = "Kaur"
kaur_liquid.size = 25
kaur_liquid.xdescribeThing("The Kaur is a thick, dark green liquid. ")
def kaurDrinkLiquid(game):
	global special_box_style
	game.addText("A warm, calm feeling spreads through you. ")
	
	kaur_ending.endGame(game)
	return True
kaur_liquid.drinkLiquid = kaurDrinkLiquid

def pickaxeUse(game):
	game.parser.command.verb = breakWithVerb
	game.parser.command.iobj = GrammarObj(target=pickaxe)
	game.parser.command.ambiguous = True
	game.addText("What would you like to break with the pickaxe? ")
	return False
pickaxe.useVerbDobj = pickaxeUse
goldingot = Thing("ingot")
goldingot.addSynonym("gold")
goldingot.setAdjectives(["gold"])
goldingot.describeThing("On the ground is a gold ingot. ")
goldingot.xdescribeThing("The ingot is made of shiny gold. ")
woodboard = Thing("plank")
woodboard.addSynonym("board")
woodboard.addSynonym("wood")
woodboard.setAdjectives(["wood", "wooden"])
woodboard._verbose_name = "wooden plank"
woodboard.size = 49
woodboard.describeThing("A wooden plank lies on the ground. ")
woodboard.xdescribeThing("The wooden plank is long and sturdy. ")
def woodboardUse(game):
	import intficpy.travel as travel
	if me.getOutermostLocation() == cave4_2:
		if not cave4_2.south:
			putAcrossVerb.verbFunc(game, woodboard, chasm4_2)
		else:
			travel.travelS(game)
	elif me.getOutermostLocation() == cave4:
		travel.travelN(game)
	else:
		game.addText("There's no obvious way of using " + woodboard.lowNameArticle(True) + " here. ")
	return False
woodboard.useVerbDobj = woodboardUse
def woodboardSetOn(game, iobj):
	if iobj==chasm4_2:
		putAcrossVerb.verbFunc(game, woodboard, chasm4_2)
		return False
	else:
		return True
woodboard.setOnVerbDobj = woodboardSetOn

# ACHIEVEMENTS
outShackAchievement = Achievement(5, "getting out of the shack")
hullAchievement = Achievement(5, "patching the hull of your boat")
sailAchievement = Achievement(5, "repairing the sail of your boat")
compassAchievement = Achievement(5, "finding a replacement compass")
combinationLockAchievement = Achievement(10, "opening the combination lock")
chasmAchievement = Achievement(5, "crossing the chasm")
curseAchievement = Achievement(5, "breaking the curse on the lower level west cavern")
puzzleBoxAchievement = Achievement(15, "opening the puzzle cube")
offeringAchievement = Achievement(25, "making the correct offering")
opalAchievement = Achievement(20, "banishing the Storm")

# Open the lock
# Open the L2 door
# Find a board
# Make a bridge
# Find a way to break the rocks
## Talk to the vendor
## Buy a pickaxe with the gold from L2
# Break the rocks in L1
# Break the rocks in L2
# Break the rocks at shore west
## "It seems you can't get any further down here for the moment. Are there any new locations on the surface you can get to, now that you have a pickaxe?
# Take the key and the journal from shore west
# Unlock door in L2
# Break the curse on the door
# Solve the puzzle cube
# enter the depths
# talk to Arai
# HINTS - PART 3

# ENDINGS
kaur_ending = Ending(True, "**YOU HAVE JOINED THE GODDESS OF THE STORM** ", "You no longer have any desire to leave the island. You enjoy the tight-knit community of your newfound home as the Storm continues to destroy everything in Her path. ")
opal_show_ending = Ending(False, "**YOU DIE** ", "Perhaps you should have heeded the warning of the woman from the shack. ")
dark_ending = Ending(False, "**YOU ARE TRAPPED IN THE DARKNESS**", "Without a light source, you are unable to find your way. No one will ever find you here. There is no escape. This is the end. ")
chasm_ending = Ending(False, "**YOU DIE**", "You fall a long way, through deepening darkness, before hitting the ground hard. You die on impact. ")
mass_murder_ending = Ending(True, "**YOU BANISH THE STORM**", "You feel yourself relax slightly as you cover the opal in earth. The feeling of a powerful presence, of being watched, which has lingered since your first encounter with the Storm, is gone. You climb back up to the surface. Arai is waiting in the ruin. She is crying. <br> \"Thank you,\" she says softly. \"And sorry. I had no right to ask this of you.\"<br> She walks with you through the streets of the town, back toward the shore. There are dead bodies everywhere you turn. Arai looks down as you walk, biting her lip. Tears flow down her face. You reach your boat. Arai looks up at you.<br> \"This place is dead,\" she says, \"But the rest of the world is safe now. You did a good thing. Don't ever forget that.\" <br> As you sail away from the Island in the Storm, bound for home at last, you can't help but wonder if there was another way  - if you could have banished the Goddess of the Storm without killing so many people. You turn your focus back to navigation. What's done is done, after all. ")
insult_goddess_ending = Ending(False, "**THE GODDESS OF THE STORM STRIKES YOU DOWN**", "The wind howls. The air is forced from your lungs, as if by a giant hand closing round you. The last thing you see before your vision fades to nothing is the enormous face of a dragon, silver-scaled and cloaked in storm clouds. The dragon rips out your soul. Your empty body falls to the ground, dead. ")
storm_inside_ending = Ending(False, "**YOU DIE IN THE STORM,**", "The walls around you creak in the roaring wind. A tree crashes through the roof. It lands on top of you, pinning you to the ground. The sky above you looks almost on fire. A silver dragon, impossibly large, dives toward you from the clouds. The Goddess roars. <br><i>YOU CANNOT HIDE FROM ME</i><br> The world goes black as the stormy dragon engulfs you. ")
storm_cave_ending = Ending(False, "**YOU DIE IN THE STORM**", "The earth rumbles around you. Dust falls from above, then pebbles, then rocks. The exit caves in. There is a resounding crack, and water starts to pour in through the crumbling ceiling. For a second, you glimpse the light of the sky above you, and the windy voice of the Storm echoes through your being. <br><i>YOU CANNOT FIGHT ME</i><br>You are crushed by the falling rocks. ")
storm_outside_ending = Ending(False, "**YOU DIE IN THE STORM**", "Lightning flashes above. It looks as if the sky has cracked open. You see the face of a silver dragon, impossibly large, among the clouds. <br><i>YOU CANNOT RUN FROM ME</i><br>As the dragon - the Goddess - fixes her eyes on you, you the strength fades from your body. Your legs give out. You lie prone in the rising water, unable to move as your life fades. Within a minute, you are dead. ")
storm_success_ending = Ending(True, "**YOU FREE THE ISLANDERS AND BANISH THE STORM**", "You feel yourself relax slightly as you cover the opal in earth. The sounds of the storm above recede into silence. The feeling of a powerful presence, of being watched, which has lingered since your first encounter with the Storm, is gone. You climb back up to the surface. Arai is waiting in the ruin. She is crying. <br> \"You did it,\" she says softly. \"You actually did it. My people are free - and alive. Well, most of them. I can't believe it.\"<br> She walks with you through the streets of the town, back toward the shore. The destruction of the Storm is visible everywhere - tree branches block paths, debris is scattered everywhere, and most of the buldings are badly damaged -  but the sun is bright, and warm on your back.<br>A woman yells to Arai as you walk past. \"What have you done, Heretic?\" she cries. <br> Arai shakes her head, smiling, and walks away. Tears flow down her face. You reach your boat. Arai looks up at you.<br> \"I would have killed them all,\" she says, \"But you found a better way. The next few years will be hard for us, here. We have a lot of work to do. But we're free. And the Storm is gone. The world is safe now.\" She hands you a power crystal. \"As promised,\" she says.<br>The boat's power system clicks back to life as you fit the crystal into the socket. Everything looks in order. <br>You push off from the shore. As you sail away, you turn to look back at the island. Arai stands on the shore, still watching you. The water is clear, and calm. You start back toward your planned route, homebound at last. ")
# CUSTOM VERBS, FUNCTIONS, AND GLOBALS

arai_death_topics = False
damage_known = False

def lensFunc(game):
	loc = me.getOutermostLocation()
	try:
		loc.lensReveal(game)
	except:
		game.addText("Looking through the lens reveals nothing you couldn't see already. ")
	return True
lens.lookThrough = lensFunc

def compassMsg():
	if not compass.location:
		return "Your compass is missing. "
	else:
		return "You still don't have your compass, but the one you found at the buried wreck should replace it well enough. "

def damageKnown(game):
	global damage_known
	damage_known = True
	mycompass.makeKnown(me)
	# picker
	picker.addSpecialTopic(picker_compass_special)
	picker.addSpecialTopic(picker_sail_special)
	picker.addSpecialTopic(picker_hull_special)
	picker.addSpecialTopic(picker_crystal_special)
	# vendor
	vendor.addSpecialTopic(vendor_compass_special)
	vendor.addSpecialTopic(vendor_sail_special)
	vendor.addSpecialTopic(vendor_hull_special)
	vendor.addSpecialTopic(vendor_crystal_special)
	##hints.setNode(fixBoatHintNode)
	#hints.closeNode(findBoatHintNode)
	
def removeSailTopics():
	picker.removeSpecialTopic(picker_sail_special)
	vendor.removeSpecialTopic(vendor_sail_special)

def removeHullTopics():
	picker.removeSpecialTopic(picker_hull_special)
	vendor.removeSpecialTopic(vendor_hull_special)

def removeCompassTopics():
	picker.removeSpecialTopic(picker_compass_special)
	#print(picker.special_topics)
	vendor.removeSpecialTopic(vendor_compass_special)

def araiWarning1(game):
	if picker.tavern_bound and picker.location != pub20:
		picker.location.removeThing(picker)
		pub20.addThing(picker)
		picker.describeThing(f"{picker.capNameArticle(True)} sits alone at a table. She smiles at you. ")
		picker.hermit_topic = None
		picker.removeAllSpecialTopics()
		picker.removeAllTopics()
		shovel.describeThing("There is a shovel here. ")
		picker.setHiTopics(picker_hi3, picker_hi4)
		picker.defaultTopic = picker_hi4.func
		shovel.invItem = True
		game.addText("Arai runs up to you as you enter the market square. \"I heard Ket invited you to the tavern,\" she says. \"She doesn't mean you any harm, but if she offers you a green drink called Kaur, don't drink it. I can't say that you'd regret it, but if you ever want to get off this island, it's the wrong thing to do. Just don't drink it, OK?\"")
		game.addText("Arai takes a few steps back, allowing you to pass. ")
		
def lightDrop(game):
	loc = me.getOutermostLocation()
	if loc.dark:
		if lightcrystal.is_lit:
			game.addText("If you drop the light crystal here, you'll never be able to find it once it dies. ")
		else:
			game.addText("You'll never find the light crystal if you drop it now. ")
		return False
	else:
		return True

lightcrystal.dropVerbDobj = lightDrop
# REPAIR WITH
# transitive verb with indirect object
repairWithVerb = Verb("repair")
repairWithVerb.addSynonym("fix")
repairWithVerb.syntax = [["repair", "<dobj>", "with", "<iobj>"], ["fix", "<dobj>", "with", "<iobj>"], ["repair", "<dobj>", "using", "<iobj>"], ["fix", "<dobj>", "using", "<iobj>"]]
repairWithVerb.hasDobj = True
repairWithVerb.dscope = "near"
repairWithVerb.hasIobj = True
repairWithVerb.iscope = "inv"
repairWithVerb.preposition = ["with", "using"]

def repairWithVerbFunc(game, dobj, iobj):
	"""Repair something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	global special_box_style
	if dobj==boat_power:
		game.addText("You won't be able to fix the power crystal using " + iobj.getArticle(True) + iobj.verbose_name + ". ")
	elif dobj==boat_sail:
		if iobj==needlethread:
			boat_sail.broken = False
			boat_sail.describeThing("The sail has been repaired. ")
			boat_sail.xdescribeThing("The sail has been repaired. ")
			game.addText("You stitch up the torn sail, using all of the thread. ")
			removeSailTopics()
			me.removeThing(iobj)
			
			sailAchievement.award(game)
			#hints.closeNode(sewSailHintNode)
			if not myboat.broken and compass.location and not boat_sail.broken:
				part1EndCut(game)
			return True
		else:
			game.addText((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " isn't the right tool for repairing the sail. ")
			return False
	elif dobj==myboat:
		if iobj==patchkit:
			myboat.broken = False
			myboat.describeThing("Your boat lies on shore. Its hull has been patched. ")
			myboat.xdescribeThing(f"You examine your boat carefully, taking stock of the damage. You have a lot to do before you'll be able to leave. {compassMsg()} The hull has been patched. ")
			game.addText("You repair the hull using the patch kit. ")
			me.removeThing(iobj)
			
			hullAchievement.award(game)
			removeHullTopics()
			#hints.closeNode(patchHullHintNode)
			if not myboat.broken and compass.location and not boat_sail.broken:
				part1EndCut(game)
			return True
		else:
			game.addText((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " isn't the right tool for repairing the damaged hull. ")
			return False
	else:
		game.addText("There's no need to repair " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False

# replace the default verbFunc method
repairWithVerb.verbFunc = repairWithVerbFunc

# REPAIR
# transitive verb
repairVerb = Verb("repair")
repairVerb.addSynonym("fix")
repairVerb.syntax = [["repair", "<dobj>"], ["fix", "<dobj>"]]
repairVerb.hasDobj = True
repairVerb.dscope = "near"

def repairVerbFunc(game, dobj):
	"""Redriect to repair with
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	if dobj==boat_power:
		game.addText("Repairing the crystal is beyond your skills. ")
	elif dobj==boat_sail or dobj==myboat:
		game.parser.command.ambiguous = True
		game.parser.command.dobj = GrammarObject(target=dobj)
		game.parser.command.verb = repairWithVerb
		game.addText("What would you like to repair it with? ")
	else:
		game.addText("There's no need to repair " + dobj.getArticle(True) + dobj.verbose_name + ". ")

# replace the default verbFunc method
repairVerb.verbFunc = repairVerbFunc

# PATCH WITH
# transitive verb with indirect object
patchWithVerb = Verb("patch")
patchWithVerb.syntax = [["patch", "<dobj>", "with", "<iobj>"], ["patch", "<dobj>", "using", "<iobj>"]]
patchWithVerb.hasDobj = True
patchWithVerb.dscope = "near"
patchWithVerb.hasIobj = True
patchWithVerb.iscope = "inv"
patchWithVerb.preposition = ["with", "using"]

def patchWithVerbFunc(game, dobj, iobj):
	"""Patch something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if iobj != patchkit:
		game.addText("You can't patch anything with " + iobj.getArticle(False) + iobj.verbose_name + ". ")
	elif dobj != myboat:
		game.addText("You cannot patch " + dobj.getArticle(False) + dobj.verbose_name + ". ")
	else:
		repairWithVerb.verbFunc(game, dobj, iobj)
	
# replace the default verbFunc method
patchWithVerb.verbFunc = patchWithVerbFunc

# PATCH (THING)
# transitive verb
patchVerb = Verb("patch")
patchVerb.syntax = [["patch", "<dobj>"]]
patchVerb.hasDobj = True
patchVerb.dscope = "near"

def patchVerbFunc(game, dobj):
	"""Patch a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	if patchkit.ix not in me.contains and patchkit.ix not in me.sub_contains:
		game.addText("You don't have a patch kit. ")
	elif dobj != myboat:
		game.addText("There's no reason to patch " + dobj.getArticle(True) + dobj.verbose_name + ". ")
	else:
		repairWithVerb.verbFunc(game, dobj, patchkit)

# replace the default verbFunc method
patchVerb.verbFunc = patchVerbFunc

# SEW WITH
# transitive verb with indirect object
sewWithVerb = Verb("sew")
sewWithVerb.addSynonym("stitch")
sewWithVerb.syntax = [["sew", "<dobj>", "with", "<iobj>"], ["stitch", "<dobj>", "with", "<iobj>"], ["sew", "<dobj>", "using", "<iobj>"], ["stitch", "<dobj>", "using", "<iobj>"]]
sewWithVerb.hasDobj = True
sewWithVerb.dscope = "near"
sewWithVerb.hasIobj = True
sewWithVerb.iscope = "inv"
sewWithVerb.preposition = ["with", "using"]

def sewWithVerbFunc(game, dobj, iobj):
	"""Sew something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if iobj != needlethread:
		game.addText("You cannot sew with " + iobj.getArticle(False) + iobj.verbose_name + ". ")
	elif dobj != boat_sail:
		game.addText("You cannot sew " + dobj.getArticle(False) + dobj.verbose_name + ". ")
	else:
		repairWithVerb.verbFunc(game, dobj, iobj)
	
# replace the default verbFunc method
sewWithVerb.verbFunc = sewWithVerbFunc

# SEW
# transitive verb
sewVerb = Verb("sew")
sewVerb.addSynonym("stitch")
sewVerb.syntax = [["sew", "<dobj>"], ["stitch", "<dobj>"]]
sewVerb.hasDobj = True
sewVerb.dscope = "near"

def sewVerbFunc(game, dobj):
	"""Sew
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	if needlethread.ix not in me.contains and needlethread.ix not in me.sub_contains:
		game.addText("You cannot sew without a needle and thread. ")
	elif dobj != boat_sail:
		game.addText("You cannot sew " + dobj.getArticle(False) + dobj.verbose_name + ". ")
	else:
		repairWithVerb.verbFunc(game, dobj, needlethread)

# replace the default verbFunc method
sewVerb.verbFunc = sewVerbFunc

# DIG WITH (shovel)
# transitive verb with indirect object
digWithVerb = Verb("dig")
digWithVerb.syntax = [["dig", "with", "<iobj>"], ["dig", "using", "<iobj>"]]
digWithVerb.hasDobj = False
digWithVerb.hasIobj = True
digWithVerb.iscope = "inv"
digWithVerb.preposition = ["with", "using"]

def digWithVerbFunc(game, iobj):
	"""Dig using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	loc = me.getOutermostLocation()
	if iobj!=shovel:
		game.addText(( iobj.getArticle(True) + iobj.verbose_name).capitalize() + " is not a good tool for digging. ")
	elif loc == shore8:
		if compass.location:
			game.addText("You've already dug here enough. ")
			return False
		else:
			game.addText("You begin to dig up the buried wreck. With the shovel, you are able to uncover much, and quickly. Most of what you find is simply debris - chunks of waterlogged wood, with the occasional mangled fastening - nothing you have any use for. You're on the verge of quitting, when your shovel scrapes agaist something smooth, and hard. You feel around the object with the shovel, before scooping it up in a clump of damp sand. <br><br>As you brush the sand from the object, you find that it is a compass.  The casing is rusty, but intact.  The inside appears dry and the needle turns smoothly. Even the calibration seems right. If Ket insists on keeping your compass, this will work as a replacement until you can get a new one. <br><br>You dig a little more, but find nothing else of value. Most likely, this wreck has already yielded all its treasures. ")
			game.addText("(Received: rusty compass)")
			shore8.floor.describeThing("The sand here is uneven from your digging. ")
			shore8.floor.xdescribeThing("The sand here is uneven from your digging. ")
			me.addThing(compass)
			global special_box_style
			
			compassAchievement.award(game)
			#hints.closeNode(digWreckHintNode)
			if not myboat.broken and compass.location and not boat_sail.broken:
				part1EndCut(game)
			return True
	elif loc == cave7:
		if not me.containsItem(opal) and not cave7.containsItem(opal):
			game.addText("You came down here to bury the opal. You should go get it before you start digging. ")
			return False
		elif not me.containsItem(opal):
			from intficpy.verb import getVerb
			game.addText("(First trying to take the opal)")
			success = getVerb.verbFunc(game, opal)
			if not success:
				return Falsef
		buryWithVerb.verbFunc(game, opal, shovel)
		return True
	else:
		game.addText("There's no reason to dig here. ")
		return False
# replace the default verbFunc method
digWithVerb.verbFunc = digWithVerbFunc

# DIG
# intransitive verb
digVerb = Verb("dig")
digVerb.syntax = [["dig"]]
digVerb.hasDobj = False
digVerb.dscope = "near"

def digVerbFunc(game):
	"""Dig
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	loc = me.getOutermostLocation()
	if shovel.ix in me.contains or shovel.ix in me.sub_contains:
		digWithVerb.verbFunc(game, shovel)
	elif loc != shore8:
		game.addText("There's no reason to dig here. ")
	elif compass.location:
		game.addText("You've already dug here enough. ")
	else:
		game.addText("You dig in the sand a bit with your hands. It's not very effective. ")

# replace the default verbFunc method
digVerb.verbFunc = digVerbFunc

# TURN TO
# transitive verb with indirect object
turnToVerb = Verb("turn")
turnToVerb.addSynonym("set")
turnToVerb.syntax = [["set", "<dobj>", "to", "<iobj>"], ["turn", "<dobj>", "to", "<iobj>"]]
turnToVerb.hasDobj = True
turnToVerb.dscope = "near"
turnToVerb.hasIobj = True
turnToVerb.iscope = "text"
turnToVerb.preposition = ["to"]

def turnToVerbFunc(game, dobj, iobj):
	"""Repair something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if dobj!=dial1:
		game.addText("There's no reason to turn " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	elif not iobj.isdigit():
		game.addText("The dial only is labeled with numbers 0 to 30. ")
		return False
	elif not (int(iobj) >= 0 and int(iobj) < 31):
		game.addText("The dial is only labeled with numbers 0 to 30. ")
		return False
	else:
		game.addText("You turn the dial. ")
		if dial1.code[dial1.cur_digit]==iobj:
			dial1.cur_digit = dial1.cur_digit + 1
			if dial1.cur_digit==4:
				c3lock.makeUnlocked()
				game.addText("You hear a loud click from the door to the east. ")
				global special_box_style
				
				#hints.closeNode(sequenceHintNode)
				combinationLockAchievement.award(game)
		else:
			dial1.cur_digit = 0

# replace the default verbFunc method
turnToVerb.verbFunc = turnToVerbFunc

# COUNT
# transitive verb
countVerb = Verb("count")
countVerb.syntax = [["count", "<dobj>"]]
countVerb.hasDobj = True
countVerb.dscope = "near"

def countVerbFunc(game, dobj):
	"""Count something
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	if dobj==nwdots:
		game.addText("You count 28 dots on the southwest monolith. ")
		return True
	else:
		game.addText("There's no reason to count that. ")

# replace the default verbFunc method
countVerb.verbFunc = countVerbFunc

# RUBBLE PROTOTYPE
rubble = Thing("rocks")
rubble.addSynonym("rock")
rubble.setAdjectives(["scattered", "crumbled"])
rubble._verbose_name = "crumbled rocks"
rubble.describeThing("Crumbled rocks are scattered across the ground. ")
rubble.xdescribeThing("Crumbled rocks are scattered across the ground. ")
rubble.invItem = False
rubble.cannotTakeMsg = "You have no use for a handful of crumbled rocks. "

# BREAK WITH
# transitive verb with indirect object
breakWithVerb = Verb("break")
breakWithVerb.syntax = [["break", "<dobj>", "with", "<iobj>"], ["break", "<dobj>", "using", "<iobj>"]]
breakWithVerb.hasDobj = True
breakWithVerb.dscope = "near"
breakWithVerb.hasIobj = True
breakWithVerb.iscope = "inv"
breakWithVerb.preposition = ["with", "using"]

def breakWithVerbFunc(game, dobj, iobj):
	"""break something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	global rock_barriers
	if dobj==cursedstar:
		breakStar(game)
	elif dobj not in rock_barriers:
		game.addText("Violence isn't the answer to this one. ")
		return False
	elif iobj == shovel:
		game.addText("Trying to break through the rocks with a shovel is more likely to destroy the shovel. ")
		return False
	elif iobj != pickaxe:
		game.addText(iobj.getArticle(True) + iobj.verbose_name + " is probably not the best tool for breaking through these rocks. ")
	else:
		game.addText("Using the pickaxe, you break through the rocks. ")
		rubble_instance = rubble.copyThing()
		dobj.location.addThing(rubble_instance)
		dobj.location.removeThing(dobj)
		try:
			dobj.crushFunc(game)
		except:
			pass
		return True
# replace the default verbFunc method
breakWithVerb.verbFunc = breakWithVerbFunc


# PUT ACROSS *(add custom func for put on, use)
# transitive verb with indirect object
putAcrossVerb = Verb("put")
putAcrossVerb.addSynonym("lay")
putAcrossVerb.syntax = [["put", "<dobj>", "across", "<iobj>"], ["put", "<dobj>", "over", "<iobj>"], ["lay", "<dobj>", "across", "<iobj>"]]
putAcrossVerb.hasDobj = True
putAcrossVerb.dscope = "inv"
putAcrossVerb.hasIobj = True
putAcrossVerb.iscope = "room"
putAcrossVerb.preposition = ["across", "over"]

def putAcrossVerbFunc(game, dobj, iobj):
	"""Lay the board across the chasm
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if dobj == woodboard and iobj == chasm4_2:
		game.addText("You lay the wooden board across the chasm. ")
		woodboard.location.removeThing(woodboard)
		cave4_2.addThing(woodboard)
		woodboard.invItem = False
		woodboard.cannotTakeMsg = "You should probably leave the board here for now. "
		woodboard.describeThing("A board has been lain across the chasm, forming a bridge. ")
		cave4_2.south = cave4
		board2 = woodboard.copyThing()
		cave4.addThing(board2)
	else:
		game.addText("There's no reason to do that. ")
# replace the default verbFunc method
putAcrossVerb.verbFunc = putAcrossVerbFunc

def _crystalCharge(game):
	global special_box_style
	loc = lightcrystal.getOutermostLocation()
	if loc.dark and not lightcrystal.is_lit and lightcrystal.turns_left:
		if me.getOutermostLocation() == loc:
			game.addText("In the darkness, the crystal starts to glow. ")
			#game.addText(str(lightcrystal.turns_left) + " turns of light remain. ")
			lightcrystal.light(game)
			loc.describe(game)
		else:
			lightcrystal.light(game)
	elif not loc.dark and lightcrystal.is_lit:
		game.addText("As it is exposed to the light, the crystal's glow fades. ")
		lightcrystal.extinguish(game)
		lightcrystal.turns_left = lightcrystal.turns_left + 1
	elif not loc.dark and lightcrystal.turns_left==(lightcrystal.max_turns - 1):
		if me.getOutermostLocation()==loc:
			game.addText("The crystal is now fully charged. ")
		lightcrystal.turns_left = lightcrystal.max_turns
	elif not loc.dark and lightcrystal.turns_left < lightcrystal.max_turns:
		lightcrystal.turns_left = lightcrystal.turns_left + 1
	elif loc.dark and not lightcrystal.turns_left and loc.dark_visible_exits==[]:
		#game.addText("It's too dark. You won't be able to find your way out. ")
		
		dark_ending.endGame(game)
crystalCharge = Daemon(_crystalCharge)

game.daemons.add(crystalCharge)

guardtower_woman = Actor("woman")
guardtower_woman.describeThing("The woman from outside kneels by the door, silently crying, eyes closed, hands clasped at her chest. \"Take me back, Goddess,\" she whispers. ")
guardtower_woman.xdescribeThing("The woman from outside kneels by the door, silently crying, eyes closed, hands clasped at her chest. \"Take me back, Goddess,\" she whispers. ")

storm_scene = 0
storm_caves = 0
def _goddessStormDaemon(game):
	global storm_turns_left
	global storm_scene
	global storm_turns_left
	global special_box_style
	if storm_turns_left:
		loc = me.getOutermostLocation()
		if storm_scene==0 and loc==road24:
			game.addText("A man runs past, holding a crying child under his soaked coat, doubtless headed for shelter. The rain pours down. ")
			storm_scene += 1
		elif storm_scene==1 and loc==square21:
			game.addText("A woman pounds frantically on the door of the guard tower to the south. \"Please!\" she cries. \"The Blessed are dead! All of them! You have to help me.\"<br>The door falls open, and she scrambles in. ")
			tower23.addThing(guardtower_woman)
			storm_scene += 1
		elif storm_scene==2 and loc==road18:
			game.addText("The trees sway dangerously in the wind. ")
			me.xdescribeThing("You are soaking wet from the rain. ")
			storm_scene += 1
		elif storm_scene==3 and loc==forest15:
			if storm_turns_full - storm_turns_left < 10:
				game.addText("The wind picks up, and it starts to hail. ")
			storm_scene += 1
		elif storm_scene==4 and loc==forest13:
			game.addText("The hailstones hit you hard, stinging your skin. ")
			storm_scene += 1
		elif storm_scene==5 and loc==cave4_2:
			game.addText("A sprinkling of sand falls from above as the earth around you shakes. ")
			storm_scene += 1
		if storm_turns_full - storm_turns_left == 10 and storm_scene < 4:
			game.addText("The wind picks up, and it starts to hail. ")
			me.xdescribeThing("You are soaking wet from the rain. ")
		if storm_turns_left == 10:
			game.addText("A crash of thunder shakes the ground. You don't have much time. ")
		if storm_turns_left == 5:
			game.addText("You feel the presence of the Goddess of the Storm, looming ever closer. ")
		game.addText(str(storm_turns_left) + " turns left. ")
		storm_turns_left -= 1
	else:
		game.addText("You have run out of time. ")
		
		if isinstance(loc, OutdoorRoom):
			storm_outside_ending.endGame(game)
		elif loc.room_group==cavegroup:
			storm_cave_ending.endGame(game)
		else:
			storm_inside_ending.endGame(game)
			
		
goddessStormDaemon = Daemon(_goddessStormDaemon)


# BURY WITH
# transitive verb with indirect object
buryWithVerb = Verb("bury")
buryWithVerb.syntax = [["bury", "<dobj>", "with", "<iobj>"], ["bury", "<dobj>", "using", "<iobj>"]]
buryWithVerb.hasDobj = True
buryWithVerb.dscope = "inv"
buryWithVerb.hasIobj = True
buryWithVerb.iscope = "inv"
buryWithVerb.preposition = ["with", "using"]

def buryWithVerbFunc(game, dobj, iobj):
	"""bury something using a tool
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	loc = me.getOutermostLocation()
	if dobj!=opal:
		game.addText("There's no reason to bury " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if loc != cave7:
		game.addText("You should go to the bottom of the caverns to bury the opal. ")
		return False
	if iobj != shovel:
		game.addText(iobj.capNameArticle(True) + " isn't the best tool for the job. ")
		return False
	game.addText("Using the shovel, you bury the opal in the ground, deep in the caverns. ")
	me.removeThing(opal)
	# CHECK FOR FREE PEOPLE
	global storm_turns_left
	global storm_turns_full
	global special_box_style
	if goddessStormDaemon in game.daemons.active:
		game.daemons.remove(goddessStormDaemon)
	
	if storm_turns_left < storm_turns_full:
		storm_success_ending.endGame(game)
	else:
		mass_murder_ending.endGame(game)
	
	opalAchievement.award(game)
# replace the default verbFunc method
buryWithVerb.verbFunc = buryWithVerbFunc

# bury
# transitive verb
buryVerb = Verb("bury")
buryVerb.syntax = [["bury", "<dobj>"]]
buryVerb.hasDobj = True
buryVerb.dscope = "inv"

def buryVerbFunc(game, dobj):
	"""Redriect to bury with
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	loc = me.getOutermostLocation()
	if dobj!=opal:
		game.addText("There's no reason to bury " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if loc != cave7:
		game.addText("You should go to the bottom of the caverns to bury the opal. ")
		return False
	if me.containsItem(shovel):
		buryWithVerb.verbFunc(game, dobj, shovel)
		return True
	else:
		game.addText("You try digging a hole in the cave floor with your hands. It's not very effective. ")
		return False

# replace the default verbFunc method
buryVerb.verbFunc = buryVerbFunc

# PRAY
# intransitive verb
prayVerb = Verb("pray")
prayVerb.syntax = [["pray"]]
prayVerb.hasDobj = False

def prayVerbFunc(game):
	"""Pray
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app """
	game.addText("You stop for a moment, and pray, to no deity in particular. ")

# replace the default verbFunc method
prayVerb.verbFunc = prayVerbFunc

# PRAY TO
# intransitive verb
prayToVerb = Verb("pray")
prayToVerb.syntax = [["pray", "to", "<iobj>"]]
prayToVerb.hasDobj = False
prayToVerb.hasIobj = True
prayToVerb.iscope = "knows"
prayToVerb.preposition = ["to"]

def prayToVerbFunc(game, iobj):
	"""Pray to a deity
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, iobj, a Thing """
	if iobj.known_ix != goddess_abs.known_ix:
		game.addText("There's no reason to pray to that. ")
		return False
	game.addText("You stop for a moment, and pray to the Goddess of the Storm. You have a sense of something vast and inhuman watching you. ")
	goddess_abs.printSuggestions(game)
	

# replace the default verbFunc method
prayToVerb.verbFunc = prayToVerbFunc

# SHACK 0 CONTINUED
window0 = Transparent("window")
window0.setAdjectives(["cracked", "dirty"])
window0.describeThing("")
window0.xdescribeThing("The window is cracked, and dirty. ")
window0.invItem = False
def window0LookThrough(game):
	if storm_turns_left < storm_turns_full:
		game.addText("So much rain is streaming down the glass that you can't see much of anything. ")
	else:
		game.addText("Outside, you can see a sandy beach, meeting the ocean to the north. ")
window0.lookThrough = window0LookThrough
shack0.addThing(window0)

arai = Actor("woman")
arai.addSynonym("heretic")
arai.describeThing(f"{arai.capNameArticle(False)} sits in a corner, reading a thick book. ")
arai.xdescribeThing(f"{arai.capNameArticle(True)} is small and slight, with dark brown hair down to her knees. ")
arai_hi1 = Topic(f"\"You're awake,\" {arai.lowNameArticle(True)} says. \"My name is Arai. I rescued you. The protective enchantment I placed on you is strong, but the Storm is stronger. You should keep your head down for now.\" ")
def araiHi1(app, suggest=True):
	game.addText(arai_hi1.text)
	arai.makeProper("Arai")
	if suggest:
		arai.printSuggestions(game)
arai_hi1.func = araiHi1
arai_book = Thing("book")
arai_book.read_desc = f"You can't see much of the text over {arai.lowNameArticle(True)}'s shoulder. "
arai_book.setAdjectives(["thick"])
arai_book.invItem = False
arai_book.describeThing("")
arai_book.xdescribeThing(f"{arai.capNameArticle(True)} is reading a thick book. ")
shack0.addThing(arai_book)
arai_hi2 = Topic(f"\"Did you need something?\"  says {arai.lowNameArticle(True)}. ")
arai.setHiTopics(arai_hi1, arai_hi2)
arai_warning2 = Topic(f"\"Just don't drink the Kaur, whatever you do,\" says {arai.lowNameArticle(True)} .")
# INTRO
arai_how = SpecialTopic("ask how you got here", f"\"I brought you here,\" says Arai. \"The Storm nearly took you, but I intervened. You're safe now.\" ")
arai_how.addAlternatePhrasing("ask how did i you get got here")
def araiHow(app, suggest=True):
	game.addText(arai_how.text)
	arai.removeSpecialTopic(arai_how)
	arai.addSpecialTopic(arai_storm_special)
	if suggest:
		arai.printSuggestions(game)
arai_how.func = araiHow
arai_us = SpecialTopic("ask what she meant by 'the likes of us'", f"\"I'm like you,\" says Arai. \"I was born here, but I'm not under Her protection either. I broke free.\" ")
def araiUs(app, suggest=True):
	game.addText(arai_us.text)
	arai.removeSpecialTopic(arai_us)
	arai.addSpecialTopic(arai_her)
	if suggest:
		arai.printSuggestions(game)
arai_us.func = araiUs
arai_storm_special = SpecialTopic("ask about the Storm", f"\"If you don't know already, I won't burden you with the knowledge,\" says Arai. \"You're better off not knowing. I wish I'd had that option.\"")
arai_storm = Topic(arai_storm_special.text)
arai.addTopic("ask", arai_storm, storm_abs)
def araiStorm(app, suggest=True):
	game.addText(arai_storm_special.text)
	arai.removeSpecialTopic(arai_storm_special)
	if suggest:
		arai.printSuggestions(game)
arai_storm_special.func = araiStorm
arai_storm.func = araiStorm
arai_key = Topic("Arai stiffens. \"That's nothing,\" she says. \"Put it back where you found it. Hell, throw it into the sea.\" She glances nervously toward the bed. ")
arai_key_special = SpecialTopic("ask about the silver key", arai_key.text)
arai_her = SpecialTopic("ask who 'Her' is", "Arai bites her lip, and looks down at her feet. ")
def araiHer(app, suggest=True):
	game.addText(arai_her.text)
	arai.removeSpecialTopic(arai_her)
	if suggest:
		arai.printSuggestions(game)
arai_her.func = araiHer
arai_leave = SpecialTopic("ask her to unlock the door", f"\"It's dangerous outside, for the likes of us,\" says Arai. \"Just stay here for now.\"")
def araiLeave(app, suggest=True):
	game.addText(arai_leave.text)
	arai.removeSpecialTopic(arai_leave)
	arai.addSpecialTopic(arai_us)
	if suggest:
		arai.printSuggestions(game)
arai_leave.func = araiLeave
# PART 1 END CUTSCENE
def part1EndCut(game):
	
	#hints.closeNode(meetKetHintNode)
	arai.location.removeThing(arai)
	#shore6.addThing(arai)
	loc = me.getOutermostLocation()
	loc.addThing(arai)
	arai.xdescribeThing("Arai looks at you thoughtfully. ")
	#arai.default_topic = arai_hi2
	arai.makeProper("Arai")
	arai.describeThing("Arai stands here, looking at you expectantly.")
	arai.xdescribeThing("Arai is small and slight, with dark brown hair down to her knees. ")
	#arai.makeProper("Arai")
	game.addText("Arai walks up to you as you finish. \"I see you've nearly finished your boat,\" she says. \"You still need a power crystal, though. I could give you one, but you'd just get killed as soon as you set sail. Unless, that is, you removed the Storm. I've been watching you. You're smart. You're resourceful. Maybe you'll be able to do what I couldn't. Maybe you can send Her back to where she came from. I can tell you exactly what to do. You just have to trust me.\" ")
	arai.hermit_topic = None
	arai.removeAllTopics()
	arai.removeAllSpecialTopics()
	arai.addSpecialTopic(arai_p2_plan)
	arai.addSpecialTopic(arai_p2_trust)
	arai.default_topic = arai_p2_default1
	arai.setHiTopics(None, None)
	arai.printSuggestions(game)
	goddess_abs.level = 2
	#hints.closeNode(fixBoatHintNode)

arai_p2_default1 = f"\"Will you help me then?\" Arai asks. \"Will you - \" she drops to a whisper here. \"Will you banish the Goddess of the Storm?\""
arai_p2_default2 = f"\"Have you been down in the caverns yet?\" Arai asks. \"The entrance is in the ruin. Just follow the path east into the woods from the road north of town.\""
arai_p2_default3 = f"\"Made any progress?\" Arai asks. \"Anything I can help you with?\""

arai_p2_plan = SpecialTopic("ask what her plan is", "Arai glances around. \"Remember the stone you took from my house?\" she says softly. \"It's the seat of the Storm's power in this world. Her domain is the sky. If we bury her vessel deep enough, she won't be able to exist in this world. She'll disappear, and this island - well, <i>we'll</i> be free. You'll have to go down to the bottom of the caves. I've cleared a lot of the traps and curses out, but what I'm asking you to do is still not exactly safe. Unfortunately, it's the only way you'll get off this island alive. Will you do it?\" ")
arai_p2_plan.addAlternatePhrasing("ask what is her your arais plan")
def araiP2Plan(app, suggest=True):
	game.addText(arai_p2_plan.text)
	arai.removeSpecialTopic(arai_p2_plan)
	arai.removeSpecialTopic(arai_p2_trust)
	arai.addSpecialTopic(arai_p2_plan2)
	arai.addSpecialTopic(arai_p2_plan3)
	arai.addSpecialTopic(arai_p2_plan4)
	if suggest:
		arai.printSuggestions(game)
arai_p2_plan.func = araiP2Plan
arai_p2_plan2 = SpecialTopic("agree to the plan", "Arai breathes a sigh of relief. \"Good,\" she says. \"The entrance to the caverns is in the ruin to the east of the mountain path - the one that runs north to south. You'll need a light source. Make sure it doesn't go out while you're down there. You'll also need this.\" Arai pulls a lens from her pocket, and holds it out for you to see. \"I've enchanted this. Looking through it will allow you to see past many common concealment charms. Use it in the first cavern to find the entrance to the rest of the caves. Beyond that, there are three levels. I've never made it to the bottom, but maybe it'll be easier for you . . . \" She trails off. Not quite looking at you, Arai continues. \"Please come talk to me if there's something you can't figure out. I don't want to make you do this alone, I just - I don't ever want to go back down there again. I'm sure it won't affect you the same way, but we'll deal with that when it comes.\" She hands you the lens. ")
def araiP2Plan2(app, suggest=True):
	#hints.closeNode(part2HintNode)
	game.addText(arai_p2_plan2.text)
	me.addThing(lens)
	game.addText("(Received: Arai's enchanted lens)")
	arai.removeSpecialTopic(arai_p2_plan2)
	arai.removeSpecialTopic(arai_p2_plan3)
	arai.removeSpecialTopic(arai_p2_plan4)
	arai.default_topic = arai_p2_default2
	if suggest:
		arai.printSuggestions(game)
arai_p2_plan2.func = araiP2Plan2
arai_p2_plan3 = SpecialTopic("tell her you need to think about it", "Arai sighs. \"Of course,\" she says. \"We're not on a deadline. Take all the time you need.\" ")
arai_p2_plan4 = SpecialTopic("refuse", f"\"I hope you'll reconsider,\" Arai says. \"I'll be here.\" ")
def araiP2Plan4(app, suggest=True):
	game.addText(arai_p2_plan4.text)
	arai.removeSpecialTopic(arai_p2_plan4)
	arai.removeSpecialTopic(arai_p2_plan3)
	if suggest:
		arai.printSuggestions(game)
arai_p2_plan4.func = araiP2Plan4
arai_p2_trust = SpecialTopic("tell her you don't trust her", f"\"Fair enough,\" Arai says. \"All the same, I hope you'll at least consider my plan.\" ")
arai_p2_trust.addAlternatePhrasing("i don't trust her you")
def araiP2Trust(app, suggest=True):
	game.addText(arai_p2_trust.text)
	arai.removeSpecialTopic(arai_p2_trust)
	if suggest:
		arai.printSuggestions(game)
arai_p2_trust.func = araiP2Trust
arai_p2_vellum1 = SpecialTopic("tell her what you learned from the vellum sheet", "Arai's face falls. \"I'm sorry,\" she says. \"I've known from the beginning. I should have told you up front. You were going to find out on your own. If the Storm is banished, Her devoted will die. I understand if you don't want to carry on with the plan, but if we work together, there might be a way we can free the islanders.\"")
def araiP2Vellum1(app, suggest=True):
	game.addText(arai_p2_vellum1.text)
	arai.removeSpecialTopic(arai_p2_vellum1)
	arai.removeSpecialTopic(arai_p2_vellum2)
	arai.addSpecialTopic(arai_p2_islanders)
	if suggest:
		arai.printSuggestions(game)
arai_p2_vellum1.func = araiP2Vellum1
arai_p2_journal1 = SpecialTopic("tell her what you learned from the journal", "Arai's face falls. \"You found my old journal, huh?\" she says. \"I'm sorry. I should have told you up front what would happen if we buried the stone. You were going to find out on your own. If the Storm is banished, Her devoted will die. I understand if you don't want to carry on with the plan, but if we work together, there might be a way we can free the islanders.\"")
def araiP2Journal1(app, suggest=True):
	game.addText(arai_p2_journal1.text)
	arai.removeSpecialTopic(arai_p2_journal1)
	arai.removeSpecialTopic(arai_p2_vellum2)
	arai.addSpecialTopic(arai_p2_islanders)
	if suggest:
		arai.printSuggestions(game)
arai_p2_journal1.func = araiP2Journal1
arai_p2_vellum2 = SpecialTopic("accuse her of trying to trick you into mass murder", "Arai sucks in her breath. \"I'm sorry,\" she says. \"I'm so sorry. Yes, they'll die if we bury the stone. Yes, I've known from the beginning. Yes, I should have told you. I understand if you don't want anything to do with me anymore, but I think there might be a way we can free the islanders. I'll be here, if you want to try.\" ")
def araiP2Vellum2(app, suggest=True):
	game.addText(arai_p2_vellum2.text)
	arai.removeSpecialTopic(arai_p2_vellum1)
	arai.removeSpecialTopic(arai_p2_journal1)
	arai.removeSpecialTopic(arai_p2_vellum2)
	arai.addSpecialTopic(arai_p2_islanders)
	if suggest:
		arai.printSuggestions(game)
arai_p2_vellum2.func = araiP2Vellum2
arai_p2_islanders = SpecialTopic("ask how the islanders can be freed", "Arai frowns. \"Most of the ways we could break the islanders' connection to the Storm from the outside risk killing them all. If we're going to get them free, we have to get the Goddess to release them Herself. As for how to do that, I'm not really sure.\" ")

arai.addSpecialTopic(arai_how)
shack0.east_wall.xdescribeThing("Against the east wall, a ladder leads upward. ")
shack0.addThing(arai)

opalbox = Container("box")
opalbox.size = 25
underbed0.addThing(opalbox)
opalbox.setAdjectives(["small", "wooden"])
opalbox.giveLid()
def openOpalBox(game):
	from intficpy.verb import openVerb
	openVerb.verbFunc(game, opalbox, True)
	if me.containsItem(opalbox) and not opaltaken:
		opalCutscene(game)
	return False
opalbox.openVerbDobj = openOpalBox

def takeOpalBox(game):
	from intficpy.verb import getVerb
	getVerb.verbFunc(game, opalbox, True)
	if opalbox.containsItem(opal) and not opaltaken  and opalbox.is_open:
		opalCutscene(game)
	return False
opalbox.getVerbDobj = takeOpalBox
	
opal = Thing("opal")
opal.size = 15

opaltaken = False
def opalCutscene(game):
	global opaltaken
	opaltaken = True
	
	if me.location==shack1:
		game.addText(f"{arai.capNameArticle(True)} emerges at the top of the ladder, a look of fury on her face. ")
	else:
		game.addText(f"{arai.capNameArticle(True)} looks up from her reading. Her eyes widen as she sees you. ")
	arai.describeThing(f"{arai.capNameArticle(True)} keeps her wide eyes fixed on you. ")
	game.addText(f"\"What have you done?\" says {arai.lowNameArticle(True)} , her voice nearly a whisper. \"You . . . you take that <i>thing</i> and get out of my house.\" <br> She grabs you by the arm, and leads you to the door. \"If you want to live, you will tell no one of what you have taken from me, or of where you found it,\" she says. <br> {arai.capNameArticle(True)} unlocks the shack door, opens it, and pushes you out. ")
	game.addText("You hear a click as the shack door locks. ")
	me.location.removeThing(me)
	shore2.addThing(me)
	global special_box_style
	
	outShackAchievement.award(game)
	##hints.setNode(findBoatHintNode)
	#hints.closeNode(shackHintNode)

def opalTake(game):
	from intficpy.verb import getVerb
	getVerb.verbFunc(game, opal, True)
	if not opaltaken:
		opalCutscene(game)
	return False
opal.getVerbDobj = opalTake
def opalGiveShow(game, dobj):
	global special_box_style
	if dobj.ix==goddess_abs.ix:
		game.addText("Nothing happens. ")
	elif dobj==arai:
		game.addText(f"\"Put that away!\" {arai.lowNameArticle(True)} hisses. ")
		return False
	elif dobj==blessed22:
		game.addText("You hold out the opal for the seven to see. For a moment, it appears they haven't noticed, but you have a sense of growing tension. You realize they've been staring at you, all of them, almost unblinking - no, literally unblinking. You glance over your shoulder to find that two of them are now behind you. When did that happen? You've been watching them the whole time. <br><br>As you turn to look back at the others, all seven step forward in unison. Their faces are empty, and impossibly still. They step forward again. You are surrounded. You need to escape. You bolt, running between the youngest and the oldest, in hopes that they will be the weakest link. The tiny girl grabs you by the wrist as you try to slip past, not even turning to look as she does so. Her grip is tight. It <i>hurts</i>, and you're no stranger to pain. <br><br>You pull against her. Your heart pounds. Her small arm rotates impossibly behind her back, but she does not budge. It is as if her humanity were simply a pretence, now abandoned. It is if <i>the restrictions of physics</i> were merely a pretense. The others gather round you once more. Each of them places a hand on your body. You try to pull away, but there is nowhere to go. Constricted by the girl's grip, your arm starts to go numb. <br><br>You fight to free yourself, but you are weakening. It must be the exhaustion of trying to resist the impossible strength of the seven - but no, that's not it. There's something else. Your heart has slowed, and the tingling has spread to most of your body. You're struggling to keep your eyes open. The life is being sucked out of you. You need to act fast - you need a plan - but your mind is dimming, along with your body. You need to get out of here. You need to get out of here. You need - ")
	elif dobj==villagers20:
		game.addText("You hold out the opal for the others in the pub to see. Everyone turns to stare stares at it. All at once, their faces go slack. A young woman stands up from her table. She pauses for a moment, before leaping at you, and tackling you to the ground. The others look on, silently. She covers your mouth with a hand, pressing you into the ground, restraining you more completely than should be possible with the weight of her body. Her strength is incredible. You fight against her with everything you have, and scream, though her hand muffles you. She does not budge. She does not flinch. She does not blink. She does not blink at all. A shiver runs through your immobilized body as you look into her eyes, and see a depth, an emptiness that cannot be human. <br><br>Your body feels wrong. The strength is draining out of you. Under the weight of this other body - this avatar - you cannot move a muscle. You cannot resist. You are utterly helpless. The world swims before you. Your vision fades. You fade. ")
	elif dobj==villagers21:
		game.addText("You hold out the opal for the villagers to see. Everyone turns to stare stares at it. All at once, their faces go slack. A young man takes a few steps toward you. He pauses for a moment, before leaping at you, and tackling you to the ground. The others look on, silently. He covers your mouth with a hand, pressing you into the ground, restraining you more completely than should be possible with the weight of her body. His strength is incredible. You fight against him with everything you have, and scream, though his hand muffles you. He does not budge. He does not flinch. He does not blink. He does not blink at all. A shiver runs through your immobilized body as you look into his eyes, and see a depth, an emptiness that cannot be human. <br><br>Your body feels wrong. The strength is draining out of you. Under the weight of this other body - this avatar - you cannot move a muscle. You cannot resist. You are utterly helpless. The world swims before you. Your vision fades. You fade. ")
	elif dobj in [vendor, picker, nurse25, daughter]:
		game.addText("You hold out the opal. " + dobj.capNameArticle(True) + " stares at it, unmoving for a moment, before leaping at you, and tackling you to the ground. She covers your mouth with a hand, pressing you into the ground, restraining you more completely than should be possible with the weight of her body. Her strength is incredible. You fight against her with everything you have, and scream, though her hand muffles you. She does not budge. She does not flinch. She does not blink. She does not blink at all. A shiver runs through your immobilized body as you look into her eyes, and see a depth, an emptiness that cannot be human. " + dobj.capNameArticle(True) + " is not the one looking out from behind those eyes. There's something else - something powerful - and it is looking directly at you. <br><br>Your body feels wrong. The strength is draining out of you. Under the weight of this other body - this avatar - you cannot move a muscle. You cannot resist. You are utterly helpless. The world swims before you. Your vision fades. You fade. ")
	elif dobj in [children21, woman21, man21]:
			return True
	elif dobj == patients25:
			game.addText("You hold out the opal for the patients to see. The nurse catches sight of it, and takes a few steps toward you. She stares at it, unmoving for a moment, before leaping at you, and tackling you to the ground. She covers your mouth with a hand, pressing you into the ground, restraining you more completely than should be possible with the weight of her body. Her strength is incredible. You fight against her with everything you have, and scream, though her hand muffles you. She does not budge. She does not flinch. She does not blink. She does not blink at all. A shiver runs through your immobilized body as you look into her eyes, and see a depth, an emptiness that cannot be human. " + dobj.capNameArticle(True) + " is not the one looking out from behind those eyes. There's something else - something powerful - and it is looking directly at you. <br><br>Your body feels wrong. The strength is draining out of you. Under the weight of this other body - this avatar - you cannot move a muscle. You cannot resist. You are utterly helpless. The world swims before you. Your vision fades. You fade. ")
	else:
		game.addText("You hold out the opal. " + dobj.capNameArticle(True) + " stares at it, unmoving for a moment, before leaping at you, and tackling you to the ground. He covers your mouth with a hand, pressing you into the ground, restraining you more completely than should be possible with the weight of his body. His strength is incredible. You fight against him with everything you have, and scream, though his hand muffles you. He does not budge. He does not flinch. He does not blink. He does not blink at all. A shiver runs through your immobilized body as you look into his eyes, and see a depth, an emptiness that cannot be human. " + dobj.capNameArticle(True) + " is not the one looking out from behind those eyes. There's something else - something powerful - and it is looking directly at you. <br><br>Your body feels wrong. The strength is draining out of you. Under the weight of this other body - this avatar - you cannot move a muscle. You cannot resist. You are utterly helpless. The world swims before you. Your vision fades. You fade. ")
	
	opal_show_ending.endGame(game)
	return False
opal.giveVerbIobj = opalGiveShow
opal.showVerbIobj = opalGiveShow
opalbox.addThing(opal)

opalbox_key = Key()
opalbox_key.setAdjectives(["silver"])
opalbox_key.taken = False
def opalboxKeyTake(game):
	if not opalbox_key.taken:
		arai.addSpecialTopic(arai_key_special)
		opalbox_key.taken = True
	return True
opalbox_key.getVerbDobj = opalboxKeyTake
opalbox_lock = Lock(True, opalbox_key)
opalbox.setLock(opalbox_lock)
arai.addTopic("asktellgiveshow", arai_key, opalbox_key)

# SHACK 1
shack1 = Room("Shack, Attic", "You are in a cramped attic. ")
shack1.storm_desc = "You are in a cramped attic. Rain pounds the roof above you. "
shackladder = LadderConnector(shack0, shack1)
shackladder.entranceA.describeThing("A ladder against the east wall leads upward. ")
shackladder.entranceB.describeThing("A ladder leads down through a hole in the floor. ")
shack0.east = shackladder
shack1.floor.xdescribeThing("A ladder leads down through a hole in the floor. ")
shelf1 = Surface("shelf")
shelf1.setAdjectives(["small"])
shack1.addThing(shelf1)
wand = Thing("baton")
wand.setAdjectives(["carved", "wooden"])
wand.describeThing("There is a carved wooden baton here. ")
wand.xdescribeThing("A delicately carved dragon spirals round the wooden baton. ")
#shelf1.addThing(wand)
#dullbook1 = Book("book", "You read a few lines. It appears to be an exceptionally dull novel. ")
#shelf1.addThing(dullbook1)
shelf1.addThing(opalbox_key)
#def atticDiscover(game):
	#arai.addSpecialTopic(arai_key_special)
#shack1.onDiscover = atticDiscover

# SHORE 2
shore2 = OutdoorRoom("Shore, Outside the Shack", "The sandy shore extends around the island to the east. A path to the southwest leads into the forest. ")
shore2.ceiling.xdescribeThing(f"{skyState()}")
shackdoor = DoorConnector(shack0, "n", shore2, "s")
shack_key = Key()
shack_key.setAdjectives(["brass"])
shack_lock = Lock(True, shack_key)
shackdoor.setLock(shack_lock)
shack0.exit = shackdoor
shackdoor.entranceB._verbose_name = "shack door"
shackdoor.entranceA.cannotOpenLockedMsg = f"The door is locked. {arai.addSpecialTopic(arai_leave)}"
shore2.w_false_msg = "The large, sharp rocks on shore block the way west from here. You can follow the beach east, or go southwest into the forest. "
shore2.n_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach east, or go southwest into the forest. "
shore2.ne_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach east, or go southwest into the forest. "
shore2.nw_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach east, or go southwest into the forest. "
shore2.se_false_msg = "The forest is too thick to go far in that direction. You can follow the beach east, or go southwest into the forest. "
rocks2 = Thing("rocks")
#shore2.addThing(pickaxe)
rocks2.setAdjectives(["large", "sharp", "west"])
rocks2.addSynonym("boulders")
rocks2.addSynonym("boulder")
rocks2.addSynonym("rock")
rocks2._verbose_name = "large rocks"
rocks2.describeThing("Large rocks block the way to the west. ")
rocks2.xdescribeThing("Large rocks block the way to the west. ")
rocks2.invItem = False
rock_barriers.append(rocks2)
def rocks2Break(game):
	game.addText("The way west is now clear. ")
	shore2.west = shore2w
rocks2.crushFunc = rocks2Break
ocean2 = Container("ocean")
ocean2.size = 500
def setInOcean(game, dobj):
	game.addText("You're not about to start dropping your possessions into the sea. ")
	return False
ocean2.setInVerbIobj = setInOcean
def dumpInOcean(game, dobj):
	if isinstance(dobj, Liquid):
		return True
	elif isinstance(dobj, Container):
		if dobj.containsLiquid():
			return True
	game.addText("You're not about to start dumping your possessions into the sea. ")
	return False
def goInOcean(game):
	if storm_turns_left==storm_turns_full:
		game.addText("You won't be able to get far without a boat. ")
	else:
		game.addText("The ocean is very rough from the storm. You don't want to get any nearer to that water. ")
		return False
ocean2.climbInVerbDobj = goInOcean 
ocean2.pourIntoVerbIobj = dumpInOcean
ocean2.desc_reveal = False
ocean2.xdesc_reveal = False
ocean2.addSynonym("sea")
shore2.addThing(ocean2)
ocean2.describeThing("To the north, the ocean stretches into the distance. ")
ocean2.storm_desc = "The ocean is rough from the storm. Large waves crash against the shore. "
ocean2.xdescribeThing("The ocean is calm today. ")
ocean2.storm_xdesc = "The ocean is rough from the storm. Large waves crash against the shore. "
ocean2.invItem = False
ocean2.holds_liquid = True
seawater2 = Liquid("seawater", "seawater")
seawater2.addSynonym("water")
seawater2.setAdjectives(["sea", "ocean", "salt"])
seawater2._verbose_name = "seawater"
seawater2.size = 450
seawater2.infinite_well = True
seawater_taken = seawater2.copyThingUniqueIx()
#seawater_taken._verbose_name = "seawater"
seawater_taken.infinite_well = False
seawater2.liquid_for_transfer = seawater_taken

def mixSeaWater(game, base_liquid, mix_in):
	container = base_liquid.getContainer()
	if not container:
		return False
	if container.name=="ocean":
		mix_in.location.removeThing(mix_in)
		game.addText("You dump " + mix_in.lowNameArticle(True) + " into the ocean. ")
		return True
	else:
		return False
seawater2.mixWith = mixSeaWater
ocean2.addThing(seawater2)
shore2.floor.addSynonym("sand")
shore2.floor.addSynonym("beach")
shore2.floor.xdescribeThing("The ground is sandy. Toward the north, it is damp from the waves. ")
shore2.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
shore2.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore2.addThing(rocks2)
forestThing2 = Thing("forest")
forestThing2.storm_xdesc = "The trees bow and creak in the wind, the storm tearing at their leaves and branches. "
shore2.addThing(forestThing2)
forestThing2.addSynonym("trees")
forestThing2.addSynonym("undergrowth")
forestThing2.invItem = False
forestThing2.describeThing("There is a thick forest to the southeast. ")
forestThing2.xdescribeThing("The trees are thick, blocking out almost all light. Beneath them, a tangle of undergrowth makes travel impossible. ")
shackoutside = Thing("shack")
shackoutside.invItem = False
shackoutside.addSynonym("wall")
shackoutside.describeThing("The shack stands to the south. ")
shore2.removeThing(shackdoor.entranceB)
shore2.addThing(shackoutside)
shackoutside.addComposite(shackdoor.entranceB)
shackdoor.entranceB.describeThing("There is a door in the middle of the wall. ")
shackdoor.entranceB._verbose_name = "shack door"
shackdoor.entranceB.xdescribeThing("You notice nothing remarkable about the door. ")
shore2.entrance = shackdoor
# SHORE 2W (Behind the sharp rocks)
shore2w = OutdoorRoom("Shore, Past the Rocks", "This patch of shore is quiet, and still. The ocean is to the north. You get the sense that you're the first person to set foot here in a long time. ")
shore2w.east = shore2
forestThing2w = forestThing2.copyThingUniqueIx()
forestThing2w.removeSynonym("tree")
shore2w.n_false_msg = "There is only ocean to the north. It probably isn't wise to try and cross it without a boat. You can only travel east from here."
shore2w.ne_false_msg = "There is only ocean to the northeast. It probably isn't wise to try and cross it without a boat. You can only travel east from here."
# east is s2
shore2w.se_false_msg = "The forest is too thick to go southeast. You can only travel east from here. "
shore2w.s_false_msg = "The forest is too thick to go south. You can only travel east from here. "
shore2w.sw_false_msg = "The forest is too thick to go southwest. You can only travel east from here. "
shore2w.w_false_msg = "The forest is too thick to go west. You can only travel east from here. "
shore2w.nw_false_msg = "There is only ocean to the northwest. It probably isn't wise to try and cross it without a boat. You can only travel east from here."
arai_journal = Book("notebook", "The first handwritten page bears the title, \"<i>Working Journal of Arai of Storm Island, Entries 314 to 322\"<br><br><b>Entry 314:</b><br> My years of research are finally paying off. I believe I have found a way to banish the Storm. It seems, hundreds of years ago, the sorcerers of this land brought Her into our world, in hopes of controlling Her power. They did this by enchanting a certain stone - an opal, the legends say - so that it might serve as a portal by which She could enter. They say that in thanks for releasing Her, the Storm has since protected the people of this island, though She does not need us. Protected! Hah. She has controlled and enslaved us. The more time I spend free of her clutches, the more clear it becomes. My people fade slowly as they age, their minds and personalities gradually becoming one with Her, until they are nothing but puppets, or empty husks, breathing but unmoving. My people become lost when they step a few metres from the path. My people are addicted, all of them, to a drink that saps their life, their motivation, and their very selves. She is not a blessing. She is not our protector. She is a tyrant, and I have discovered how to defeat her, at long last. When buried deep in the earth, the opal will lose its power. Its enchantment will fade, and She will lose Her ability to manifest Herself in this world. We will be free. All of us. We will be free, and I will be able to return to my family, at long last.  <i><br><br><b>Entry 315:</b><br>I have located the opal. The priests keep it in a box, in the Hall of the Blessed. I am going to steal it. It shouldn't be difficult. Nobody ever steals here, so there aren't many protections in place. I will report back tomorrow. Wish me luck. <br><br><b>Entry 316</b><br>I have the opal. No one saw me take it. I should be fine, as long as I keep it hidden. Since the opal's disappearance, She has seized control of any follower who so much as sees something that looks like it. It doesn't matter. I just have to be smart. Moving on to the next phase of my plan. Will report back. <br><br><b>Entry 316:</b><br>I have been exploring the caves. The lens I enchanted a year ago has come in very handy. I think if I can get to the bottom, it will be deep enough. Cracked the code for the east room today. <br><br><b>Entry 317:</b><br> Entered the west room today. Found some disappointing news. I've been oversimplifying things a little. Turns out, if I just bury the opal, everyone on this island will die, because of their connection to the Storm. This is going to slow me down a bit, but I'll figure it out. If I broke out, surely I can figure out how to get the rest of us free. Will report back.  <i><br><br><b>Entry 318:</b> Feeling a bit hopeless. I managed to convince a friend to stop drinking the Kaur. She's the only one so far. I was hoping she would be an example that others would follow, but things are not going well. Her withdrawal so far has been a lot worse than mine. I guess I weaned myself off over a long time. I didn't realise how much difference it would make. She's been screaming, and trembing, and crying. Last night, her father brought her Kaur, and she drank. She was pretty mad at me, once she was lucid again. I don't think she'll trust me anymore. I don't think anyone's going to trust me anymore. I'll have to act without their cooperation. <br><br><b>Entry 319:</b><br> I used to put up an energetic shield, when I wanted time away from the Storm. When my connection to Her finally broke, I was shielded. I'd also been off Kaur for a month, but it was the shield that did it, I think. I'm going to try shielding some of the villagers. Wish me luck. <br><br><b>Entry 320:</b><br>I can't do this. I don't think there's any way. I held four villagers within my shield. They cried, and screamed, and prayed to be freed. After an hour, I saw one of their connections break - that of a young boy. I removed the shield, to see what would happen. Within seconds, the Storm struck him down. He was 10 years old. No one saw what I did, but I'm drowning in guilt. I give up. I give up. I have half a mind to drink the Kaur myself, and beg the Goddess for the Blessed Peace.  <i><br><br><b>Entry 321</b><br>She took another boat today. It's happening more and more often. I think her reach is growing. I don't know what's out there, but maybe the rest of the world can be saved. I know for sure Her devoted can't. I'm going to banish the Goddess of the Storm, even if everyone on this island dies because of me. <br><br><b>Entry 322</b><br>I can't do it. I got into the west room on the bottom level. I can't. I can't. I know it's just a curse - just an illusion, but it's too much for me. I'm never going back there. I lost control of my magic, down in the caves - caused a minor cave in. I wish I'd been crushed, so I wouldn't have to decide whether to live this useless life, or die for my shame. I will remain on this island until I die, and the Storm will rage through the world, destorying everything in Her path. I have failed. I have failed. I have failed. </i><br><br> You have reached the end of the notebook. ")
arai_journal.addSynonym("book")
arai_journal.addSynonym("journal")
arai_journal.setAdjectives(["leather", "bound", "note", "arais"])
arai_journal._verbose_name = "leather bound notebook"
arai_journal.describeThing("On the ground is a leather bound notebook. ")
arai_journal.xdescribeThing("The leather bound notebook is worn. ")
def araiJournalRead(game):
	global arai_death_topics
	game.addText(arai_journal.read_desc)
	if not arai_death_topics:
		arai_death_topics = True
		arai.addSpecialTopic(arai_p2_journal1)
		arai.addSpecialTopic(arai_p2_vellum2)
arai_journal.readText = araiJournalRead
s2wbox = Container("box")
s2wbox.setAdjectives(["rough", "wooden"])
s2wbox.size = 39
s2wbox.giveLid()
s2wbox.makeClosed()
tree2w = UnderSpace("tree")
tree2w.setAdjectives(["very", "tall", "old"])
tree2w._verbose_name = "tall old tree"
tree2w.invItem = False
tree2w.revealed = True
tree2w.describeThing("At the edge of the woods is a tree, very old, and very tall. ")
shore2w.addThing(tree2w)
shore2w.floor.addSynonym("sand")
shore2w.floor.addSynonym("beach")
shore2w.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
shore2w.floor.xdescribeThing("The ground is sandy. Toward the north, it is damp from the waves. ")
shore2w.floor.cannotTakeMsg = "You have no use for a handful of sand. "
ocean2w = ocean2.copyThingUniqueIx()
seawater2w = seawater2.copyThing()
shore2w.addThing(ocean2w)
ocean2w.addThing(seawater2w)
llwkey = Key()
llwkey.setAdjectives(["tarnished", "brass"])
llwkey.xdescribeThing("The key is made of tarnished brass. ")

def shore2wReveal(game):
	if s2wbox.location:
		game.addText("Looking through the lens reveals nothing further. ")
		return True
	else:
		game.addText("Looking through the lens reveals a rough wooden box at the base of the tree. ")
		tree2w.addThing(s2wbox)
		s2wbox.addThing(arai_journal)
		#s2wbox.addThing(wand)
		s2wbox.addThing(llwkey)
		return True
shore2w.lensReveal = shore2wReveal

# SHORE 3
shore3 = OutdoorRoom("Shore, East of the Shack", "The sandy shore extends around the island to the west and southeast. ")
shore3.ceiling.xdescribeThing(f"{skyState()}")
shore3.west = shore2
shore2.east = shore3
shore3.s_false_msg = "The forest is too thick to go far in that direction. You can follow the beach west, or southeast. "
shore3.sw_false_msg = "The forest is too thick to go far in that direction. You can follow the beach west, or southeast. "
shore3.n_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach west, or southeast. "
shore3.ne_false_msg = "There is only ocean to the northeast. It's probably not wise to try and cross it without a boat. You can follow the beach west, or southeast. "
shore3.nw_false_msg = "The there is only ocean to the northwest. It's probably not wise to try and cross it without a boat. You can follow the beach west, or southeast. "
shore3.e_false_msg = "The there is only ocean to the east. It's probably not wise to try and cross it without a boat. You can follow the beach west, or southeast. "
ocean3 = ocean2.copyThingUniqueIx()
shore3.addThing(ocean3)
seawater3 = seawater2.copyThing()
ocean3.addThing(seawater3)
shore3.floor.addSynonym("sand")
shore3.floor.addSynonym("beach")
shore3.floor.xdescribeThing("The ground is sandy. Toward the north, it is damp from the waves. ")
shore3.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore3.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
forestThing3 = forestThing2.copyThingUniqueIx()
forestThing3.describeThing("There is a thick forest to the south. ")
shore3.addThing(forestThing3)
#shore3.addThing(arai_journal)

# SHORE 4 (WRECK SITE 1)
shore4 = OutdoorRoom("Shore, Site of a Long Ago Wreck", "The sandy shore extends around the island to the southeast and northwest. ")
shore4.ceiling.xdescribeThing(f"{skyState()}")
shore4.northwest = shore3
shore3.southeast = shore4
shore4.s_false_msg = "The forest is too thick to go far in that direction. You can follow the beach southeast, or northwest. "
shore4.sw_false_msg = "The forest is too thick to go far in that direction. You can follow the beach southeast, or northwest. "
shore4.w_false_msg = "The forest is too thick to go far in that direction. You can follow the beach southeast, or northwest. "
shore4.n_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach southeast, or northwest. "
shore4.ne_false_msg = "There is only ocean to the northeast. It's probably not wise to try and cross it without a boat. You can follow the beach southeast, or northwest. "
shore4.e_false_msg = "The there is only ocean to the east. It's probably not wise to try and cross it without a boat. You can follow the beach southeast, or northwest. "
ocean4 = ocean2.copyThingUniqueIx()
ocean4.describeThing("To the northeast, the ocean stretches into the distance. ")
shore4.addThing(ocean4)
seawater4 = seawater2.copyThing()
ocean4.addThing(seawater4)
shore4.floor.addSynonym("sand")
shore4.floor.addSynonym("beach")
shore4.floor.xdescribeThing("The ground is sandy. Toward the northeast, it is damp from the waves. ")
shore4.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore4.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
wreck1 = Thing("wreck")
wreck1.addSynonym("shipwreck")
wreck1.addSynonym("ship")
wreck1.setAdjectives(["long", "ago", "old", "ship", "wrecked"])
wreck1._verbose_name = "old wreck"
wreck1.describeThing("The last remains of a long ago shipwreck are scattered across the sand.")
wreck1.xdescribeThing("The old wreck has been thoroughly picked over. You can barely tell it was ever a ship.")
wreck1.invItem = False
wreck1.cannotTakeMsg = "The last remains of this wreck are scattered across the shore. You doubt there's anything of value left here. "
shore4.addThing(wreck1)
forestThing4 = forestThing2.copyThingUniqueIx()
forestThing4.describeThing("There is a thick forest to the southwest. ")

# SHORE 5
shore5 = OutdoorRoom("Shore, East Side of the Island", "The sandy shore extends around the island to the south and northwest. ")
shore5.ceiling.xdescribeThing(f"{skyState()}")
shore5.northwest = shore4
shore4.southeast = shore5
shore5.sw_false_msg = "The forest is too thick to go far in that direction. You can follow the beach south, or northwest. "
shore5.w_false_msg = "The forest is too thick to go far in that direction. You can follow the beach south, or northwest. "
shore5.n_false_msg = "The there is only ocean to the north. It's probably not wise to try and cross it without a boat. You can follow the beach south, or northwest. "
shore5.ne_false_msg = "There is only ocean to the northeast. It's probably not wise to try and cross it without a boat. You can follow the beach south, or northwest. "
shore5.e_false_msg = "The there is only ocean to the east. It's probably not wise to try and cross it without a boat. You can follow the beach south, or northwest. "
shore5.se_false_msg = "The there is only ocean to the southeast. It's probably not wise to try and cross it without a boat. You can follow the beach south, or northwest. "
ocean5 = ocean2.copyThingUniqueIx()
ocean5.describeThing("To the east, the ocean stretches into the distance. ")
shore5.addThing(ocean5)
seawater5 = seawater2.copyThing()
ocean5.addThing(seawater5)
shore5.floor.addSynonym("sand")
shore5.floor.addSynonym("beach")
shore5.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
shore5.floor.xdescribeThing("The ground is sandy. Toward the east, it is damp from the waves. ")
shore5.floor.cannotTakeMsg = "You have no use for a handful of sand. "
forestThing5 = forestThing2.copyThingUniqueIx()
forestThing5.describeThing("There is a thick forest to the west. ")

# SHORE 6 (CRASH SITE)
shore6 = OutdoorRoom("Shore, Crash Site", "The sandy shore extends around the island to the north. ")
shore6.ceiling.xdescribeThing(f"{skyState()}")
shore6.north = shore5
shore5.south = shore6
shore6.sw_false_msg = "The forest is too thick to go far in that direction. You can go back along the beach to the north. "
shore6.s_false_msg = "The forest is too thick to go far in that direction. You can go back along the beach to the north. "
shore6.w_false_msg = "The forest is too thick to go far in that direction. You can go back along the beach to the north. "
shore6.nw_false_msg = "The forest is too thick to go far in that direction. You can go back along the beach to the north. "
shore6.ne_false_msg = "There is only ocean to the northeast. It's probably not wise to try and cross it without a boat. You can go back along the beach to the north. "
shore6.e_false_msg = "The there is only ocean to the east. It's probably not wise to try and cross it without a boat. You can go back along the beach to the north. "
shore6.se_false_msg = "The there is only ocean to the southeast. It's probably not wise to try and cross it without a boat. You can go back along the beach to the north. "
ocean6 = ocean5.copyThingUniqueIx()
shore6.addThing(ocean6)
seawater6 = seawater2.copyThing()
ocean6.addThing(seawater6)
shore6.floor.addSynonym("sand")
shore6.floor.addSynonym("beach")
shore6.floor.xdescribeThing("The ground is sandy. Toward the east, it is damp from the waves. ")
shore6.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore6.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
shore6.onDiscover = damageKnown
forestThing6 = forestThing5.copyThingUniqueIx()

myboat.setAdjectives(["my", "your"])
myboat.addSynonym("hull")
myboat.has_proper_name = True
myboat.invItem = False
myboat._verbose_name = "your boat"
myboat.cannotTakeMsg = "The boat is too big to carry. It'll have to stay here until you can repair it. "
myboat.describeThing(f"Your boat lies on shore, with a hole in its hull. {compassMsg()} ")
myboat.xdescribeThing("You examine your boat carefully, taking stock of the damage. You have a lot to do before you'll be able to leave. {compassMsg()} There is a hole in the hull. ")
myboat.broken = True
shore6.addThing(myboat)
myboat.addThing(lightcrystal)
def getinboat(game):
	game.addText("There's no use in getting in the boat right now. It's not as if you can sail it in its current state. ")
	return False
myboat.climbInVerbDobj = getinboat

boat_sail.setAdjectives(["torn", "boat"])
boat_sail._verbose_name = "torn sail"
boat_sail.describeThing("The sail is torn. ")
boat_sail.xdescribeThing("The sail is torn. ")
boat_sail.broken = True
myboat.addComposite(boat_sail)
boat_mast = Thing("mast")
boat_mast.setAdjectives(["boat"])
boat_mast._verbose_name = "mast"
boat_mast.describeThing("")
boat_mast.xdescribeThing("The mast is undamaged. ")
myboat.addComposite(boat_mast)
power_slot = Container("socket")
power_slot.setAdjectives(["power", "crystal"])
def crystalSlotDesc():
	if boat_power.ix in power_slot.contains:
		return "In the boat's crystal socket, the power crystal is badly cracked. "
	else:
		return "The boat's crystal socket is empty. "

boat_power.setAdjectives(["broken", "cracked", "power"])
boat_power.addSynonym("power")
boat_power._verbose_name = "cracked power crystal"
boat_power.describeThing("")
boat_power.xdescribeThing("The power crystal is badly cracked. There's no chance you'll be able to use it in its current state. ")
def putInSlotFunc(game, dobj):
	if dobj==boat_power:
		game.addText("You fit the power crystal back into its slot. ")
		#me.contains[dobj.ix].remove(dobj)
		me.removeThing(dobj)
		power_slot.addThing(boat_power)
		return False
	elif dobj==lightcrystal:
		game.addText("While the light crystal is made of the same material as a power crystal, the enchantment is different, making the energy output much lower. Unfortunately it won't work well as a power source. ")
		return False
	else:
		game.addText("Trying to fit " + dobj.getArticle(True) + dobj.verbose_name + " inside might damage the socket's conductive coating. ")
		return False
power_slot.setInVerbIobj = putInSlotFunc
power_slot.describeThing(f"{crystalSlotDesc()}")
power_slot.xdescribeThing(f"{crystalSlotDesc()}")
myboat.addComposite(power_slot)
power_slot.addThing(boat_power)

# FOREST PATH 7, NE
forest7 = OutdoorRoom("Forest Path, Northeast End", "The path runs from the northeast, sloping upward to the southwest. ")
forest7.ceiling.xdescribeThing(f"{skyState()}")
forest7.northeast = shore2
shore2.southwest = forest7
forest7.n_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and southwest from here. The forest to the west looks thin enough to be passable. "
forest7.e_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and southwest from here. The forest to the west looks thin enough to be passable. "
forest7.se_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and southwest from here. The forest to the west looks thin enough to be passable. "
forest7.s_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and southwest from here. The forest to the west looks thin enough to be passable. "
forest7.nw_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and southwest from here. The forest to the west looks thin enough to be passable. "
forest7.floor.addSynonym("path")
forest7.floor.xdescribeThing("The path here is narrow, and overgrown. ")
forestThing7 = forestThing5.copyThingUniqueIx()
forestThing7.describeThing("A lush, green forest grows on both sides of the path. Sunlight filters in through the canopy of leaves. The undergrowth is dense, but seems thinner to the west. ")
forest7.storm_desc = "The thick forest is nearly black in the dark of the storm. The trees sway dangerously in the wind. "
forestThing7.xdescribeThing("The trees here are old, and tall. The undergrowth is dense, and tangled, but thins a bit to the west. ")
forest7.addThing(forestThing7)

# SHORE 8 (WRECK SITE 2)
shore8 = OutdoorRoom("Shore, Site of a Half-Buried Wreck", "There is a short patch of sand along the shore. ")
def shore8Arrive(game):
	##hints.setNode(shovelHintNode)
	#hints.closeNode(findWreckHintNode)
	pass
shore8.arriveFunc = shore8Arrive
shore8.ceiling.xdescribeThing(f"{skyState()}")
shore8.east = forest7
forest7.west = shore8
shore8.s_false_msg = "The forest is too thick to go far in that direction. You can return to the path to the east. "
shore8.sw_false_msg = "The forest is too thick to go far in that direction. You can return to the path to the east. "
shore8.ne_false_msg = "The forest is too thick to go far in that direction. You can return to the path to the east. "
shore8.se_false_msg = "The forest is too thick to go far in that direction. You can return to the path to the east. "
shore8.nw_false_msg = "There is only ocean to the northwest. It's probably not wise to try and cross it without a boat. You can return to the path to the east. "
shore8.w_false_msg = "The there is only ocean to the west. It's probably not wise to try and cross it without a boat. You can return to the path to the east. "
ocean8 = ocean2.copyThingUniqueIx()
ocean8.describeThing("To the northwest, the ocean stretches into the distance. ")
shore8.addThing(ocean8)
seawater8 = seawater2.copyThing()
ocean8.addThing(seawater8)
shore8.floor.addSynonym("sand")
shore8.floor.addSynonym("beach")
shore8.floor.xdescribeThing("The ground is sandy. Toward the northwest, it is damp from the waves. ")
shore8.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore8.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
forestThing8 = forestThing2.copyThingUniqueIx()
forestThing8.describeThing("A thick forest surrounds the section of beach on three sides. It is a bit thinner to the east. ")
forestThing8.xdescribeThing("The trees are thick, blocking out almost all light. Beneath them, a tangle of undergrowth makes travel impossible. It looks like you might be able to get through to the east. ")
shore8.addThing(forestThing8)
wreck2 = Thing("wreck")
wreck2.addSynonym("shipwreck")
wreck2.addSynonym("boat")
wreck2.addSynonym("bow")
wreck2.setAdjectives(["buried", "old", "ship", "wrecked"])
wreck2._verbose_name = "buried wreck"
wreck2.describeThing("The broken bow of an old boat sticks up out of the sand. It's clearly been here a long time. ")
wreck2.xdescribeThing("The boat is half buried in the sand. What you can see is in very bad shape. The hull is broken clean through, and pieces are scattered across the beach. ")
wreck2.invItem = False
wreck2.cannotTakeMsg = "Even if you managed to free the boat, it would be too large to carry. "
shore8.addThing(wreck2)

# FOREST PATH 9, BEND
forest9 = OutdoorRoom("Forest Path, Bend", "The path bends around the hillside here, from the northeast, to the south, leading upward. ")
forest9.ceiling.xdescribeThing(f"{skyState()}")
forest9.northeast = forest7
forest7.southwest = forest9
forest9.n_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and south. A cave opens to the east. "
forest9.nw_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and south. A cave opens to the east. "
forest9.w_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and south. A cave opens to the east. "
forest9.se_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and south. A cave opens to the east. "
forest9.sw_false_msg = "The forest is too thick to go far in that direction. The path leads northeast, and south. A cave opens to the east. "
forest9.floor.addSynonym("path")
forest9.floor.xdescribeThing("The path here is narrow, and overgrown. ")
forestThing9 = forestThing5.copyThingUniqueIx()
forestThing9.describeThing("A lush, green forest grows on both sides of the path. ")
forest9.storm_desc = "The forest on either side of the path is thick and dark. The trees tremble and quake against the violent winds. "
forestThing9.xdescribeThing("The trees here are old, and tall. The undergrowth is dense, and tangled. ")
forest9.addThing(forestThing9)

# SMALL CAVE 10
smallCave10 = Room("Small Cavern, off the Forest Path", "The cave is small, perhaps two metres across. The ceiling is only just higher than your head. ")
smallCave10.dark = True
smallCave10.dark_visible_exits = ["w", "exit"]
smallCaveConnector = TravelConnector(forest9, "e", smallCave10, "w")
smallCaveConnector.entranceA.setAdjectives(["east", "small", "cliff", "cave", "hole", "in", "rock", "rough"])
smallCaveConnector.entranceA.name = "cave"
smallCaveConnector.entranceA.removeSynonym("doorway")
smallCaveConnector.entranceA.addSynonym("face")
smallCaveConnector.entranceA.addSynonym("rock")
smallCaveConnector.entranceA.addSynonym("hole")
smallCaveConnector.entranceA.addSynonym("cliff")
smallCaveConnector.entranceA._verbose_name = "small cave"
smallCaveConnector.entranceA.describeThing("A cliff peaks out through the trees to the east, just off the path. A rough hole in the rock face looks large enough for you to pass through.")
smallCaveConnector.entranceA.xdescribeThing("The rock face is rough, extending up, high above you. The hole looks large enough for you to pass through. ")
smallCaveConnector.entranceA_msg = "You crawl into the cave."
smallCaveConnector.entranceB.name = "hole"
smallCaveConnector.entranceB.removeSynonym("doorway")
smallCaveConnector.entranceB.addSynonym("outside")
smallCaveConnector.entranceB.addSynonym("hole")
smallCaveConnector.entranceB.setAdjectives(["west", "hole", "leading"])
smallCaveConnector.entranceB._verbose_name = "hole leading outside"
smallCaveConnector.entranceB_msg = "You crawl out of the cave."
smallCaveConnector.entranceB.describeThing("Light trickles in through a hole to the west.")
smallCaveConnector.entranceB.xdescribeThing("The hole looks large enough for you to pass through. ")
for item in smallCave10.walls:
	item.xdescribeThing("The cave wall is rough stone. ")
	item.setAdjectives(item.adjectives + ["cave"])
	item.describeThing("")
forest9.entrance = smallCaveConnector
smallCave10.exit = smallCaveConnector
copper1 = Thing("coin")
copper1.size = 2
copper1.setAdjectives(["small", "copper"])
copper1._verbose_name = "copper coin"
copper1.describeThing("On the ground is a copper coin. ")
copper1.xdescribeThing("The coin is small, and made of copper. ")

def copper1Take(game):
	if copper1.ix in me.contains or copper1.ix in me.sub_contains:
		##hints.setNode(sewSailHintNode)
		#hints.closeNode(findCopperHintNode)
		pass
	return True

copper1.getVerbDobj = copper1Take
	

smallCave10.addThing(copper1)

# FOREST PATH 11, SLOPE
forest11 = OutdoorRoom("Forest Path, Across a Slope", "The path, carved across a steep slope, runs north to south. ")
forest11.ceiling.xdescribeThing(f"{skyState()}")
forest11.north = forest9
forest9.south = forest11
forest11.w_false_msg = "The slope to the west is too steep to descend safely. You can follow the path north or south from here, or take the faint trail to the east leading up the slope. "
forest11.sw_false_msg = "The forest is too thick to go far in that direction. You can follow the path north or south from here, or take the faint trail to the east leading up the slope. "
forest11.nw_false_msg = "The forest is too thick to go far in that direction. You can follow the path north or south from here, or take the faint trail to the east leading up the slope. "
forest11.ne_false_msg = "The forest is too thick to go far in that direction. You can follow the path north or south from here, or take the faint trail to the east leading up the slope. "
forest11.nw_false_msg = "The forest is too thick to go far in that direction. You can follow the path north or south from here, or take the faint trail to the east leading up the slope. "
forest11.floor.setAdjectives(["main"])
forest11.floor.addSynonym("path")
forest11.floor._verbose_name = "main path"
forest11.floor.describeThing("")
forest11.floor.xdescribeThing("The path here is narrow, and overgrown. ")
forestThing11 = forestThing5.copyThingUniqueIx()
forestThing11.describeThing("Forest grows thick on the downward slope to the west of the path, and a bit thinner on the eastern side. Directly east of you, a faint trail meanders up the mountain. It looks passable. ")
forestThing11.xdescribeThing("The trees here are old, and tall. ")
forest11.storm_desc = "The forest is thick as dark around you. The leaves  flail in the wind, loud as an angry sea. "
forest11.addThing(forestThing11)

# FOREST 12, UPHILL
forest12 = OutdoorRoom("Forest, Uphill of the Path", "The path, narrow, and overgrown, bends here. To the west, it leads down the hill, toward the main path. To the south, it leads deeper into the forest. ")
forest12.ceiling.xdescribeThing(f"{skyState()}")
path12 = TravelConnector(forest11, "u", forest12, "w", "path")
path12.entranceA.setAdjectives(["east", f"aint", "meandering", "steep"])
path12.entranceA.name = "trail"
path12.entranceA.addSynonym("mountain")
path12.entranceA._verbose_name = "faint trail"
path12.entranceA.describeThing("")
path12.entranceA.xdescribeThing("The trail is faint, and steep. ")
path12.entranceA_msg = "You struggle your way up the faint trail."
path12.entranceB.name = "trail"
path12.entranceB.addSynonym("path")
path12.entranceB.addSynonym("trail")
path12.entranceB.setAdjectives(["faint", "steep", "trail", "leading", "back"])
path12.entranceB._verbose_name = "trail leading back down"
path12.entranceB_msg = "You struggle down the faint trail. "
path12.entranceB.describeThing("")
path12.entranceB.xdescribeThing("The trail is faint, and steep. ")
forest12.down = path12
forest11.east = path12
forest12.sw_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.se_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.nw_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.ne_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.n_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.e_false_msg = "The trail here bends from west to south. You'll get lost if you wander away from it. "
forest12.floor.addSynonym("path")
forest12.floor.addSynonym("grass")
forest12.floor.xdescribeThing("The path here can barely be called a path at all. It is narrow, and grassy, nearly disappearing in some places.")
forestThing12 = forestThing5.copyThingUniqueIx()
forestThing12.describeThing("Forest grows thick, and green all around you. ")
forestThing12.storm_desc = "The trees around you creak and bow in the storm winds. "
forestThing12.xdescribeThing("The trees here are old, and tall. ")
forest12.addThing(forestThing12)

# FOREST 13, DEEP IN THE FOREST
forest13 = OutdoorRoom("Deep in the Forest", "You are deep in the forest. The trail, visible only with careful scrutiny, disappears into the woods to the north and east. ")
forest13.ceiling.xdescribeThing(f"{skyState()}")
forest13.north = forest12
forest12.south = forest13
forest13.sw_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore. "
forest13.se_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore.  "
forest13.nw_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore.  "
forest13.ne_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore.  "
forest13.w_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore.  "
forest13.s_false_msg = "The trail leads north and east. You're in danger of getting lost as it is. If you lose the path now, you might never find your way back to shore.  "
forest13.floor.addSynonym("path")
forest13.floor.addSynonym("trail")
forest13.floor.addSynonym("grass")
forest13.floor.xdescribeThing("The path here can barely be called a path at all. It is narrow, and grassy, nearly disappearing in some places.")
forestThing13 = forestThing5.copyThingUniqueIx()
forestThing13.setAdjectives(["ancient", "old", "enormous"])
forestThing13._verbose_name = "ancient trees"
forestThing13.describeThing("All around you, enormous, ancient trees grow. You see nothing but forest in all directions. ")
forestThing13.storm_desc = "All around you, enormous, ancient trees grow. In the dark of the storm, you can barely see more than a metre into the woods. "
forestThing13.xdescribeThing("The trees here are old, and tall. ")
forest13.addThing(forestThing13)

# TEMPLE 14, ABANDONED TEMPLE
temple14 = OutdoorRoom("Ruin", "You find yourself in what appears to be a long-abandoned temple. A trail leads into the woods to the west. ")
temple14.ceiling.xdescribeThing(f"{skyState()}")
#temple14.north = cave0
forest13.east = temple14
temple14.west = forest13
temple14.e_false_msg = "The forest is too dense to go far in that direction. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.s_false_msg = "The forest is too dense to go far in that direction. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.sw_false_msg = "A carved monolith blocks the way. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.se_false_msg = "A carved monolith blocks the way. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.nw_false_msg = "A carved monolith blocks the way. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.se_false_msg = "A carved monolith blocks the way. You can get back onto the trail to the west, or enter the cave to the north. "
temple14.floor.addSynonym("stones")
temple14.floor.addSynonym("dragon")
temple14.floor.addSynonym("tail")
temple14.floor.addSynonym("floor")
temple14.floor.addSynonym("grass")
temple14.floor.describeThing("The ground is a mosaic of stones, in greys, and earthy reds, coming together into an image of a dragon, circling the ruin. ")
temple14.floor.storm_desc = "The stone-tiled ground is slick with water. "
temple14.floor.storm_xdesc = "The stone-tiled ground is slick with water. "

cave_entrance14 = Thing("cave")
cave_entrance14.describeThing("To the north is the entrance to a cave. ")
cave_entrance14.xdescribeThing("To the north is the entrance to a cave. ")
cave_entrance14.direction = "in"
cave_entrance14.invItem = False
temple14.addThing(cave_entrance14)

def mainCavesEnter(game):
	from intficpy.travel import travelN
	travelN(game)
cave_entrance14.climbInVerbDobj = mainCavesEnter

def viewDragon():
	pass
	#hints.closeNode(dragonHintNode)
	#if pillarsHintNode.complete:
		#hints.closeNode(ruinHintNode)
		

temple14.floor.xdescribeThing(f"Grass springs up between the stones of the floor. In the pattern of the tiles, you can see the image of a silver dragon, flying through a red sky. Starting from the tail in the northwest, it circles clockwise round the ruin. {viewDragon()}")
templeThing14 = Thing("ruin")
templeThing14.describeThing("")
templeThing14.xdescribeThing("The stones of the floor are cracked, and grass has sprung up between. The ruin is clearly very old.")
templeThing14.invItem = False
temple14.addThing(templeThing14)
forestThing14 = forestThing5.copyThingUniqueIx()
forestThing14.setAdjectives(["old"])
forestThing14._verbose_name = "old forest"
forestThing14.describeThing("An old forest encircles the ruin. ")
forestThing14.xdescribeThing("The trees here are old, and tall. ")
temple14.addThing(forestThing14)
monoliths14 = []
m14adj = ["northwest", "northeast", "southeast", "southwest"]
for adj in m14adj:
	monolith = Thing("monolith")
	monolith.addSynonym("stone")
	monolith.addSynonym("stones")
	monolith.addSynonym("monoliths")
	monolith.setAdjectives(["great", "stone", adj])
	monolith._verbose_name = adj + " monolith"
	monolith.describeThing("")
	monolith.xdescribeThing("The monolith is tall. ") # REPLACE THIS FOR PUZZLE
	monolith.invItem = False
	monolith.cannotTakeMsg = "The monolith is taller than you are, and made of solid stone. You can't possibly move it. "
	monoliths14.append(monolith)
	temple14.addThing(monolith)

xmonoliths = []
def viewMonolith(n):
	global xmonoliths
	if n not in xmonoliths:
		pass
		#xmonoliths.append(n)
		#hints.setNode(pillarsHintNode)
		#if len(xmonoliths) == 4:
			#hints.closeNode(pillarsHintNode)
			#if dragonHintNode.complete:
				#hints.closeNode(ruinHintNode)

monoliths14[0].describeThing("At each of the four corners of the ruin stands a great stone monolith. ")
monoliths14[0].xdescribeThing(f"Carved into the northwest monolith is a triangle of 3 dots. {viewMonolith(0)}")
monoliths14[1].xdescribeThing(f"Carved into the northeast monolith is a triangle of 6 dots. {viewMonolith(1)}")
monoliths14[2].xdescribeThing(f"Carved into the southeast monolith is an equilateral triangle formed of 15 evenly spaced dots. {viewMonolith(2)}")
monoliths14[3].xdescribeThing(f"Carved into the southwest monolith is an equilateral triangle of evenly spaced dots, arranged in an isometric pattern. Each side is made up of 7 dots. The total number of dots is too great to be immediately apparent. {viewMonolith(3)}")
nwdots = Thing("dots")
nwdots.xdescribeThing("The dots are arranged in an isometric, triangular grid. ")
nwdots.describeThing("")
nwdots.invItem = False
temple14.addThing(nwdots)
# FOREST PATH 15, MOUNTAINSIDE
forest15 = OutdoorRoom("Forest Path, Mountainside", "The path runs north to south. ")
forest15.ceiling.xdescribeThing(f"{skyState()}")
forest15.north = forest11
forest11.south = forest15
forest15.u_false_msg = "The slope to the east is too steep to ascend safely. The path here leads north and south. You might be able to climb down the mountain to the west. "
forest15.e_false_msg = "The slope to the east is too steep to ascend safely. The path here leads north and south. You might be able to climb down the mountain to the west."
forest15.sw_false_msg = "The slope to the southwest looks too steep to descend safely. The path here leads north and south. You might be able to climb down the mountain to the west."
forest15.nw_false_msg = "There aren't many good handholds on the slope to the southwest. The path here leads north and south. You might be able to climb down the mountain to the west."
forest15.ne_false_msg = "The slope is too steep to ascend safely in that direction. The path here leads north and south. You might be able to climb down the mountain to the west."
forest15.nw_false_msg = "The slope is too steep to ascend safely in that direction. The path here leads north and south. You might be able to climb down the mountain to the west."
forest15.floor.setAdjectives(["main"])
forest15.floor.addSynonym("path")
forest15.floor._verbose_name = "main path"
forest15.floor.describeThing("")
forest15.floor.xdescribeThing("The path here is narrow, and overgrown. ")
forestThing15 = forestThing5.copyThingUniqueIx()
forestThing15.setAdjectives(["thin", "fallen"])
forestThing15.addSynonym("roots")
forestThing15.describeThing("The forest is all around you. It isn't as thick here as in other places, and thins even more to the east of the path, where the upward slope is steep.")
forestThing15.xdescribeThing("The trees here are thin, growing straight upward from the diagonal ground. A few have fallen. Roots are exposed in places.")
forest15.addThing(forestThing15)
mountainThing15 = Thing("peak")
mountainThing15.addSynonym("mountain")
mountainThing15.describeThing("Above the treetops to the east, the peak of a mountain is visible. ")
mountainThing15.xdescribeThing("Above the treetops to the east, the peak of a mountain is visible. ")
mountainThing15.invItem = False
mountainThing15.direction = "u"
#mountainThing15.far_away = True
forest15.addThing(mountainThing15)
mountainThing15.addSynonym("slope")
mountainThing15._verbose_name = "mountain"
def slope15upfunc(game):
	game.addText("The slope to the east is too steep to ascend safely. ")
	return False
def slope15downfunc(game):
	import intficpy.travel as travel
	travel.travelW(game)
	return False
mountainThing15.climbOnVerbDobj = slope15upfunc
mountainThing15.climbDownFromVerbDobj = slope15downfunc

# FOREST 16, DOWNHILL
forest16 = OutdoorRoom("Forest, Downhill", "The path is uphill to the east. To the west, light shines in through the trees. ")
forest16.ceiling.xdescribeThing(f"{skyState()}")
forest16.storm_desc = "The path is uphill to the east. To the west, thick trees are buffeted by the storm. "
mountainThing16 = LadderConnector(forest16, forest15)
mountainThing16.entranceA.name = "mountain"
mountainThing16.entranceA.addSynonym("mountain")
mountainThing16.entranceA.addSynonym("slope")
mountainThing16.entranceA.removeSynonym("ladder")
mountainThing16.entranceA.setAdjectives(["upward", "mountain", "east"])
mountainThing16.entranceA._verbose_name = "upward slope"
mountainThing16.entranceA.describeThing("")
mountainThing16.entranceA.xdescribeThing("The slope is gentle, and dotted with trees. You should be able to climb it with no trouble. ")
mountainThing16.entranceA_msg = "You climb up the slope. "
mountainThing16.entranceB_msg = "You climb down the slope. "
mountainThing16.entranceB.name = "mountain"
mountainThing16.entranceB.addSynonym("mountain")
mountainThing16.entranceB.addSynonym("slope")
mountainThing16.entranceB.removeSynonym("ladder")
mountainThing16.entranceB.setAdjectives(["downward", "west"])
mountainThing16.entranceB._verbose_name = "downward slope"
mountainThing16.entranceB.describeThing("The ground slopes downward to the west. ")
mountainThing16.entranceB.xdescribeThing("The ground slopes downward to the west. ")
forest16.east = mountainThing16
forest15.west = mountainThing16

forest16.s_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.n_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.sw_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.nw_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.ne_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.nw_false_msg = "The forest is too thick to go far in that direction. It looks like you can go east, or west from here. "
forest16.floor.setAdjectives(["fallen", "forest"])
forest16.floor.addSynonym("floor")
forest16.floor.addSynonym("leaves")
forest16.floor.describeThing("")
forest16.floor.xdescribeThing("The ground is covered in fallen leaves. It slopes downward to the west. ")
forest16.floor._verbose_name = "forest floor"
forestThing16 = forestThing5.copyThingUniqueIx()
forestThing16.setAdjectives(["thin", "fallen"])
forestThing16.describeThing("The forest is all around you. The slope is less steep here, and the trees grow in thicker. ")
forestThing16.storm_desc = "The thick forest is black in the dark of the clouded sky. "
forestThing16.xdescribeThing("The trees grow on an angle here. The undergrowth is thick. ")
forest16.addThing(forestThing16)

# SHORE 17 (BASE OF THE MOUNTAIN)
shore17 = OutdoorRoom("Shore, Base of the Mountain", "The ground here flattens out into a small beach. ")
shore17.ceiling.xdescribeThing(f"{skyState()}")
mountainThing17 = LadderConnector(shore17, forest16)
mountainThing17.entranceA.name = "mountain"
mountainThing17.entranceA.addSynonym("mountain")
mountainThing17.entranceA.addSynonym("slope")
mountainThing17.entranceA.addSynonym("base")
mountainThing17.entranceA.removeSynonym("ladder")
mountainThing17.entranceA.setAdjectives(["base", "of", "mountain"])
mountainThing17.entranceA._verbose_name = "mountain slope"
mountainThing17.entranceA.describeThing("Forest surrounds you on three sides. To the east, where the trees are thinner, you can see the base of the mountain you have just descended. The slope is gentle enough that you should be able to climb it with no trouble. ")
mountainThing17.entranceA.xdescribeThing("The slope is gentle, and dotted with trees. You should be able to climb it with no trouble. ")
mountainThing17.entranceA_msg = "You climb up the slope. "
mountainThing17.entranceB_msg = "You climb down the slope. "
mountainThing17.entranceB.name = "mountain"
mountainThing17.entranceB.addSynonym("mountain")
mountainThing17.entranceB.addSynonym("slope")
mountainThing17.entranceB.removeSynonym("ladder")
mountainThing17.entranceB.setAdjectives(["downward", "west"])
mountainThing17.entranceB._verbose_name = "downward slope"
mountainThing17.entranceB.describeThing("The ground slopes downward to the west. ")
mountainThing17.entranceB.xdescribeThing("The ground slopes downward to the west. ")
shore17.east = mountainThing17
forest16.west = mountainThing17

shore17.s_false_msg = "The forest is too thick to go far in that direction. You can start back up the mountain to the east. "
shore17.sw_false_msg = "The there is only ocean to the southwest. It's probably not wise to try and cross it without a boat. You can start back up the mountain to the east. "
shore17.ne_false_msg = "The forest is too thick to go far in that direction. You can start back up the mountain to the east. "
shore17.se_false_msg = "The forest is too thick to go far in that direction. You can start back up the mountain to the east. "
shore17.s_false_msg = "The forest is too thick to go far in that direction. You can start back up the mountain to the east. "
shore17.nw_false_msg = "There is only ocean to the northwest. It's probably not wise to try and cross it without a boat. You can start back up the mountain to the east. "
shore17.w_false_msg = "The there is only ocean to the west. It's probably not wise to try and cross it without a boat. You can start back up the mountain to the east. "
ocean17 = ocean2.copyThingUniqueIx()
ocean17.describeThing("To the west, the ocean stretches into the distance. ")
shore17.addThing(ocean17)
seawater17 = seawater2.copyThing()
ocean17.addThing(seawater17)
shore17.floor.addSynonym("sand")
shore17.floor.addSynonym("beach")
shore17.floor.xdescribeThing("The ground is sandy. Toward the west, it is damp from the waves. ")
shore17.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore17.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
forestThing17 = forestThing2.copyThingUniqueIx()
forestThing17.describeThing("")
forestThing17.xdescribeThing("The trees are thick, blocking out almost all light. Beneath them, a tangle of undergrowth makes travel impossible. It looks like you can get through to the east. ")
shore17.addThing(forestThing17)
daughter = Actor("woman")
daughter.addSynonym("girl")
daughter.setAdjectives(["young", "lost"])
daughter._verbose_name = "young woman"
daughter.describeThing("A young woman in a green dress stands here. ")
daughter.xdescribeThing(f"{daughter.capNameArticle(True)} is tall, with short black hair. She is wearing a pale green dress. ")
daughter_father = SpecialTopic("ask if she's the boatmaker's daughter", f"{daughter.capNameArticle(True)} looks at you directly for the first time. \"My father,\" she says, a look of instense concentration on her face. \"He'll be missing me. I must get back to him.\" She pauses, blinking a few times, as if to clear her eyes. \"You aren't lost, are you? Somehow, you've managed to stray from the path without losing your way . . . . What a strange power  . . . you have.\" She trails off. After a long silence, she takes a deep breath, and looks you directly in the eye. \"Lead me,\" she says. \"Lead me home. Please.\" ")
daughter_father.addAlternatePhrasing("ask if are you is she the boatmakers boat makers daughter")
def daughterFather(app, suggest=True):
	game.addText(daughter_father.text)
	daughter.removeSpecialTopic(daughter_father)
	boatmaker.addSpecialTopic(boatmaker_daughter2_special)
	daughter.can_be_led = True
	daughter.default_topic = daughter_default2
	daughter.makeProper("Tani the Boatmaker's Daughter")
daughter_father.func = daughterFather
daughter.default_topic = f"{daughter.capNameArticle(True)} doesn't seem to hear, or even see you. \"I've strayed from the path,\" she mutters. \"I am lost. I am forever lost. Oh, Goddess, let me die swiftly.\""
shore17.addThing(daughter)
daughter_composites = [Thing("hair"), Thing("dress")]
daughter_composites[0].setAdjectives(["young", "tanis", "womans", "girls", "short", "black"])
daughter_composites[1].setAdjectives(["young", "tanis", "womans", "girls", "pale", "green"])
daughter_composites[0]._verbose_name = "the young woman's hair"
daughter_composites[1]._verbose_name = "the young woman's dress"
daughter_composites[0].xdescribeThing(f"{daughter.capNameArticle(True)} 's hair is short and black. ")
daughter_composites[1].xdescribeThing(f"{daughter.capNameArticle(True)} 's dress is pale green. ")
for item in daughter_composites:
	item.describeThing("")
	daughter.addComposite(item)
daughter_composites[0].cannotTakeMsg = "You can't take someone's hair! "
daughter_composites[1].cannotTakeMsg = "You can't take someone's clothing! "

daughter_default2 = f"\"Please take me to my father,\" says {daughter.lowNameArticle(True)} . \"He will be missing me.\" "
daughter_default3 = f"\"Thank you for your help,\" says {daughter.lowNameArticle(True)} . \"Now, I need some time to rest.\" "

boatmaker_default2 = f"\"Thank you for rescuing my daughter,\" says the boatmaker. \"If there's anything else I can do for you, please let me know.\" "
boatmaker_board_special = SpecialTopic("ask for a wooden plank to make a bridge", f"\"Sure, I can give you a plank of wood,\" says the boatmaker. \"Just gimme a second.\" He disappears behind the ship for a moment, and returns with a wooden board on his shoulder. \"Here you are, then.\"")
def boatmakerBoard(app, suggest=True):
	game.addText(boatmaker_board_special.text)
	me.addThing(woodboard)
	game.addText("(Received: " + woodboard.verbose_name + ")")
	boatmaker.removeSpecialTopic(boatmaker_board_special)
boatmaker_board_special.func = boatmakerBoard

def boatmakerDefault2(app, suggest=True):
	game.addText(boatmaker_default2)
	if suggest:
		boatmaker.printSuggestions(game)

def daughterLead(game, iobj):
	from intficpy.verb import leadDirVerb
	leadDirVerb.verbFunc(game, daughter, iobj, True)
	return False

daughter.leadDirVerbDobj = daughterLead

# ROAD 18 (Cobblestone Road, Base of Mountain)
road18 = OutdoorRoom("Cobblestone Road, Base of the Mountain", "A cobblestone road leads north, and southeast. ")
road18.ceiling.xdescribeThing(f"{skyState()}")
road18.storm_desc = "A cobblestone road leads north, and southeast. Rain water flows across it. "
mountainThing18 = TravelConnector(road18, "u", forest15, "s", "slope", 2)
mountainThing18.entranceA._verbose_name = "upward slope"
mountainThing18.entranceA.addSynonym("mountain")
mountainThing18.entranceA.describeThing("")
mountainThing18.entranceA.xdescribeThing("A mountain rises to the north. ")
mountainThing18.entranceB._verbose_name = "downward slope"
mountainThing18.entranceB.describeThing("")
mountainThing18.entranceB.xdescribeThing("The ground slopes downward to the south . ")

road18.north = mountainThing18
road18.s_false_msg = "There is only farmland to the south. You can go north, into the forest, or southeast, into town. "
road18.sw_false_msg = "There is only farmland to the southwest. You can go north, into the forest, or southeast, into town. "
road18.ne_false_msg = "The forest is too thick to go far in that direction. You can go north, into the forest, or southeast, into town.  "
road18.e_false_msg = "The forest is too thick to go far in that direction. You can go north, into the forest, or southeast, into town.  "
road18.nw_false_msg = "The forest is too thick to go far in that direction. You can go north, into the forest, or southeast, into town.  "
road18.w_false_msg = "The forest is too thick to go far in that direction. You can go north, into the forest, or southeast, into town.  "
road18.floor.addSynonym("road")
road18.floor.addSynonym("cobblestones")
road18.floor.setAdjectives(["cobblestone"])
road18.floor.xdescribeThing("The road is made of cobblestones. ")
road18.floor.storm_xdesc = "Muddy water flows across the cobblestones. "
road18.floor.describeThing("")
forestThing18 = forestThing2.copyThingUniqueIx()
forestThing18.setAdjectives(["lush", "green"])
forestThing18.describeThing("There is forest to the east and west, and on the mountain to the north. To the south, it dissolves into farmland. ")
forestThing18.storm_desc = "Wind tears at the forest to the east and west, and north, and at the farms to the south. "
forestThing18.xdescribeThing("The trees are lush, and green. ")
road18.addThing(forestThing18)
farmThing18 = Thing("farmland")
farmThing18.invItem = False
farmThing18.addSynonym("farms")
farmThing18.addSynonym("farm")
farmThing18.describeThing("")
farmThing18.xdescribeThing("The farmland looks fertile, and well-tended. ")
road18.addThing(farmThing18)
townThing18 = Thing("town")
townThing18.addSynonym("village")
townThing18.setAdjectives(["small"])
townThing18.invItem = False
townThing18.describeThing("")
townThing18.xdescribeThing("The village is small, with buildings of wood and stone. ")
def go_in_town(game):
	import intficpy.travel as travel
	travel.travelSE(game)
townThing18.climbInVerbDobj = go_in_town
road18.addThing(townThing18)

# MARKET 19 (Market Square)
market19 = OutdoorRoom("Market Square", "In a wide square, paved with cobblestones, a small market has been set up.  Roads from the square lead northwest, toward the edge of town, and east. There is a small, wooden building to the south. ")
market19.ceiling.xdescribeThing("f{skyState()}")
market19.storm_desc = "The market square is mostly abandoned. Roads from the square lead northwest, toward the edge of town, and east. There is a small, wooden building to the south. "
road18.southeast = market19
market19.northwest = road18
market19.sw_false_msg = "There is only farmland to the southwest. You can go northwest, east, or south. "
market19.ne_false_msg = "You can only go northwest, east, or south from here. "
market19.w_false_msg = "There is only farmland to the west. You can go northwest, east, or south.  "
market19.n_false_msg = "The forest is too thick to go far in that direction. You can go northwest, east, or south. "
market19.floor.addSynonym("square")
market19.floor.addSynonym("cobblestones")
market19.floor.setAdjectives(["cobblestone"])
market19.floor.xdescribeThing("The square is paved with cobblestones. ")
market19.floor.describeThing("")
market19.addThing(townThing18)
forestThing19 = forestThing2.copyThingUniqueIx()
forestThing19.setAdjectives(["lush", "green"])
forestThing19.describeThing("There is a forest to the north, and farmland to the west. ")
forestThing19.xdescribeThing("The trees are lush, and green. ")
market19.addThing(forestThing19)
farmThing19 = farmThing18.copyThingUniqueIx()
farmThing19.xdescribeThing("The farmland looks fertile, and well-tended. ")
market19.addThing(farmThing19)
marketThing19 = Thing("market")
marketThing19.addSynonym("stalls")
marketThing19.setAdjectives(["market"])
marketThing19.invItem = False
marketThing19.describeThing("")
marketThing19.xdescribeThing("There are a few stalls set up around the square. ")
marketThing19.storm_xdesc = "A few stalls are left here. Some have collapsed from the wind, and all but one is abandoned. "
market19.addThing(marketThing19)
stallThing19 = Thing("stall")
stallThing19.setAdjectives(["market"])
stallThing19.invItem = False
stallThing19.describeThing("")
stallThing19.xdescribeThing("Bright fabrics and sewing notions hang from the market stall. ")
stallThing19.storm_desc = "The fabrics that hangs from the market stall are soaked with rainwater. "
sewingNotions19 = Thing("notions")
sewingNotions19.has_proper_name = True
sewingNotions19.addSynonym("needles")
sewingNotions19.addSynonym("thread")
sewingNotions19.addSynonym("buttons")
sewingNotions19.addSynonym("needle")
sewingNotions19.invItem = False
sewingNotions19.cannotTakeMsg = "You aren't going to steal from the stall when the proprietor is right here! "
sewingNotions19.setAdjectives(["sewing"])
sewingNotions19.describeThing("")
sewingNotions19.xdescribeThing("Needles and buttons have been strung onto lengths of colourful thread, and hung from the stall. ")
sewingNotions19.known_ix = needlethread.ix
fabric19 = Thing(f"abrics")
fabric19.addSynonym("fabric")
fabric19.addSynonym("taffeta")
fabric19.addSynonym("crepe")
fabric19.setAdjectives(["bright", "red", "pale", "green"])
fabric19._verbose_name = "bright fabric"
fabric19.invItem = False
fabric19.cannotTakeMsg = "You aren't going to steal from the stall when the proprietor is right here! "
fabric19.describeThing("")
fabric19.xdescribeThing("Bright fabrics and sewing notions hang from the market stall. ")
market19.addThing(stallThing19)
market19.addThing(sewingNotions19)
market19.addThing(fabric19)
vendor = Actor("vendor")
vendor.storm_desc = "The vendor you bought from earlier cowers beneath the inadequate shelter of her toppled stall's canvas roof. Eyes squeezed shut, trembling hands clamped over her ears, she sobs. "
vendor.storm_xdesc = "The vendor you bought from earlier cowers beneath the inadequate shelter of her toppled stall's canvas roof. Eyes squeezed shut, trembling hands clamped over her ears, she sobs. "
vendor.storm_hermit_state = Topic(f"\"The Goddess has left us,\" the vendor breathes. \"And now she would kill us. Leave me to die in peace, Outsider.\" ")
vendor.describeThing("One vendor, at a stall hung with fabrics and sewing notions, waves at you. ")
vendor.xdescribeThing("The vendor is a stout, middle-aged woman with curly hair. She smiles nercously as you stare. ")
market19.addThing(vendor)
vendor_notions = Topic(f"\"I'll sell you a needle and thread for two copper,\" says the vendor. ")
def vendorNotions(app, suggest=True):
	game.addText(vendor_notions.text)
	if suggest:
		vendor.printSuggestions(game)
vendor_notions.func = vendorNotions
vendor.addTopic("asktell", vendor_notions, needlethread)
vendor_fabrics = Topic("The vendor smiles. \"Hmm,\" she says. \"Well, personally, I'm partial to this red taffeta. Oh, but the pale green crepe is lovely, too! You can't go wrong, really.\" ")
vendor.addTopic("asktell", vendor_fabrics, fabric19)
vendor.default_topic = f"\"Is there something I can help you with?\" the vendor asks. "
vendor_sail = Topic(f"\"A torn sail, you say?\" says the vendor. \"Well, I can sell you a sharp needle and some good strong thread for two copper. That oughta help you fix it up.\"")
vendor.addTopic("asktell", vendor_sail, boat_sail)
vendor_sail_special = SpecialTopic("tell the vendor about your torn sail", vendor_sail.text)
def vendorSail(app, suggest=True):
	#hints.closeNode(talkVendorHintNode)
	game.addText(vendor_sail_special.text)
	if suggest:
		vendor.printSuggestions(game)
vendor_sail.func = vendorSail
vendor_sail_special.func = vendorSail
vendor_sail_special.addAlternatePhrasing("tell her him vendor about my your torn sail")
vendor_hull = Topic(f"\"You should talk to Sem, in the shipyard,\" says the vendor. \"He's our master boatmaker. He'd know what to do.\" ")
def vendorHull(app, suggest=True):
	game.addText(vendor_hull.text)
	boatmaker.makeProper("Sem the Boatmaker")
	vendor.printSuggestions(game)
	#hints.setNode(talkBoatmakerHintNode)
vendor.addTopic("asktell", vendor_hull, myboat)
vendor_hull_special = SpecialTopic("tell the vendor about your the hole in your hull", vendor_hull.text)
vendor_hull.func = vendorHull
vendor_hull_special.func = vendorHull
vendor_hull_special.addAlternatePhrasing("tell her him vendor about hole in my your broken boat hull")
vendor_crystal = Topic(f"\"Hmm,\" says the vendor. \"Well, I don't know much about boats, but I don't think we use anything like your 'power crystal' here. Your best bet is probably going to the Hall of the Blessed. Yes, I'm sure the Blessed will know how to fix it. They know just about everything.\" The vendor smiles. ")
vendor.addTopic("asktellgiveshow", vendor_crystal, boat_power)
vendor_crystal_special = SpecialTopic("tell the vendor about your broken power crystal", vendor_crystal.text)
vendor_crystal_special.addAlternatePhrasing("tell her him vendor about my your broken boat power crystal source")
def vendorCrystal(app, suggest=True):
	blessed22.addSpecialTopic(blessed_crystal_special)
	game.addText(vendor_crystal.text)
	vendor.printSuggestions(game)
vendor_crystal.func = vendorCrystal
vendor_crystal_special.func = vendorCrystal
vendor_compass = Topic(f"\"Your compass went missing from your boat?\" says the vendor. \"I wonder if Ket picked it up. She collects parts from shipwrecks. She might not have realized the boat's owner was still alive. You should go talk to her in the scrapyard. I'm sure she'd be happy to give it back, if she has it.\" ")
def vendorCompass(app, suggest=True):
	game.addText(vendor_compass.text)
	vendor.printSuggestions(game)
	#hints.setNode(talkPickerHintNode)
vendor.addTopic("asktell", vendor_compass, mycompass)
vendor_compass_special = SpecialTopic("tell the vendor about your missing compass", vendor_compass.text)
vendor_compass_special.addAlternatePhrasing("tell her him vendor about my your missing compass")
vendor_compass.func = vendorCompass
vendor_compass_special.func = vendorCompass
vendor.addSelling(needlethread, copper1, 2, 1)
vendor.for_sale[needlethread.ix].out_stock_msg = "You don't need another needle and thread. "
def needleAfterBuy(game):
	#hints.closeNode(buyNeedleHintNode)
	pass
vendor.for_sale[needlethread.ix].afterBuy = needleAfterBuy
#vendor.addWillBuy(needlethread, copper1, 2, 1)
vendor.addSelling(pickaxe, goldingot, 1, 1)
vendor.for_sale[pickaxe.ix].out_stock_msg = "You don't need another pickaxe. "
vendor_pickaxe = Topic(f"\"I can sell you a pickaxe, if you can come up with a gold ingot,\" says the vendor.")
vendor_pickaxe_special = SpecialTopic("ask if she sells a tool for breaking boulders", vendor_pickaxe.text)
vendor_pickaxe_special.addAlternatePhrasing("ask her vendor if do you sell a tool tools for breaking boulders rocks")
def vendorBoulderAsk(game):
    game.addText(vendor_pickaxe.text)
    vendor.printSuggestions(game)
    pickaxe.makeKnown(me)
vendor_pickaxe.func = vendorBoulderAsk
vendor_pickaxe_special.func = vendorBoulderAsk

buildingThing19 = Thing("building")
buildingThing19.invItem = False
buildingThing19.setAdjectives(["small", "wooden"])
buildingThing19.describeThing("")
buildingThing19.xdescribeThing("The building is small, and wooden. ")
market19.addThing(buildingThing19)
def go_in_building19(game):
	import intficpy.travel as travel
	travel.travelS(game)
buildingThing19.climbInVerbDobj = go_in_building19
#market19.addThing(lens)
# PUB 20
pub20 = Room("Village Pub", "This small, wooden building appears to be the village pub. It is oddly still, and silent inside. In seated around two tables, villagers silently sip on a pungent smelling beverage. A few appear to be passed out. No one seems alarmed by this. ")
pub20.storm_desc = "The walls of the little wooden building rattled creak in the wind. The patrons are in a state of disarray. Some cower in corners. Others scream and cry. "
pub20.north = market19
pub20.exit = market19
market19.south = pub20
tables20 = Thing("tables")
tables20.invItem = False
tables20.addSynonym("table")
tables20.setAdjectives(["dark", "wood", "wooden", "old", "pub"])
tables20._verbose_name = "pub tables"
tables20.describeThing("")
tables20.xdescribeThing("The pub tables are old, and made of dark wood. ")
pub20.addThing(tables20)
def pub_tables_set(game, dobj):
	game.addText("A villager glares at you warningly, and you withdraw your hand. ")
	return False
tables20.setOnVerbIobj = pub_tables_set
villagers20 = Actor("villagers")
villagers20.addSynonym("people")
villagers20.addSynonym("villager")
villagers20.setAdjectives(["passed", "out"])
villagers20.describeThing("")
villagers20.xdescribeThing("The villagers are clustered around two tables. A few are passed out. ")
villagers20.storm_xdesc = "The villagers look frightened. "
pub20.addThing(villagers20)
villagers20.default_topic = "A few of the more alert villagers look up at you. You get a smile or two, and a few sleepy nods, but no one speaks. "
kaur_offering_topic = SpecialTopic("ask for Kaur to make an offering", "Ket the Picker's face lights up. \"Of course!\" she says. \"Here!\" She hands you a cup of Kaur. ")
def kaurOfferingTopic(app, suggest=True):
	game.addText(kaur_offering_topic.text)
	me.addThing(kaur_cup)
	kaur_cup.addThing(kaur_liquid)
	game.addText("(Received: white ceramic cup containing Kaur)")
	picker.removeSpecialTopic(kaur_offering_topic)
	#villagers20.removeSpecialTopic(kaur_offering_topic)
kaur_offering_topic.func = kaurOfferingTopic
drink20 = Thing("beverage")
drink20.addSynonym("drink")
drink20.addSynonym("liquid")
drink20.addSynonym("cups")
drink20.addSynonym("kaur")
drink20.setAdjectives(["thick", "dark", "green", "drink", "in", "villagers"])
drink20._verbose_name = "drink in the villagers' cups"
drink20.describeThing("")
drink20.xdescribeThing("You catch a glimpse of the drink over the shoulder of one of the villagers. It appears to be a thick, dark green liquid. ")
drink20.invItem = False
drink20.cannotTakeMsg = "You're not about to grab the drink from a villager's hand. "
pub20.addThing(drink20)

# SQUARE 21 (Town Square)
square21 = OutdoorRoom("Town Square", "Here, roads lead east and west from a wide, cobblestone square. To the north is an ornately built hall. To the south is a stone watchtower. ")
square21.storm_desc = "Here, roads lead east and west from a wide, cobblestone square. To the north is an ornately built hall. To the south is a stone watchtower. The ground is slick with rain. "
square21.ceiling.xdescribeThing(f"{skyState()}")
square21.west = market19
market19.east = square21
square21.sw_false_msg = "You can only go north, east, west, or south from here."
square21.ne_false_msg = "You can only go north, east, west, or south from here. "
square21.se_false_msg = "You can only go north, east, west, or south from here."
square21.nw_false_msg = "You can only go north, east, west, or south from here. "
square21.floor.addSynonym("square")
square21.floor.addSynonym("cobblestones")
square21.floor.setAdjectives(["cobblestone"])
square21.floor.xdescribeThing("The square is paved with cobblestones. ")
square21.floor.describeThing("")
square21.addThing(townThing18)
hallThing21 = Thing("hall")
hallThing21.invItem = False
hallThing21.addSynonym("building")
hallThing21.setAdjectives(["north", "ornate", "ornately", "built"])
hallThing21._verbose_name = "ornately built hall"
hallThing21.describeThing("")
hallThing21.xdescribeThing("The hall is ornately built, with decorative swirls carved into the wood of its facade, and bright stained glass windows. ")
square21.addThing(hallThing21)
def go_in_hall21(game):
	import intficpy.travel as travel
	travel.travelN(game)
hallThing21.climbInVerbDobj = go_in_hall21
towerThing21 = Thing("watchtower")
towerThing21.addSynonym("building")
towerThing21.addSynonym("tower")
towerThing21.invItem = False
towerThing21.setAdjectives(["watch", "stone"])
towerThing21._verbose_name = "stone watchtower"
towerThing21.describeThing("")
towerThing21.xdescribeThing("The tower, constructed from large slabs of stone, looks like a fortess compared to the wooden buildings surrounding it. At the top, you can see the silhouette of someone standing beneath a raised roof. ")
square21.addThing(towerThing21)
def go_in_tower(game):
	import intficpy.travel as travel
	travel.travelS(game)
towerThing21.climbInVerbDobj = go_in_tower
villagers21 = Actor("villagers")
villagers21.addSynonym("people")
villagers21.invItem = False
def squareVillagersFunc():
	desc = ["A group of villagers are passing through. They stop to gawk at you for a moment before continuing on their way. ", "Three villagers stand in the corner of the square, chatting idly. Another few walk past, headed east. ", "Four children chase each other through the square, laughing. They stop when they catch sight of you, and, noticing that you are looking at them, hurry away. ", "A young man pushes a barrow of fruits through the square, toward the market, whistling as he walks. ", "A woman with a baby walks past. A child runs to catch up with her. She takes his hand as they pass out of the square. "]
	return random.choice(desc)
villagers21.describeThing(f"{squareVillagersFunc()}")
villagers21.xdescribeThing(f"{squareVillagersFunc()}")
villagers21.storm_desc = "The once busy square is abandoned. "
villagers21.storm_xdesc = "There's no one here. "
villagers21.default_topic = "The villagers appear too occupied to pay you much heed. "
square21.addThing(villagers21)
children21 = Actor("children")
children21.setAdjectives(["four"])
children21.ignore_if_ambiguous = True
children21.describeThing("")
children21.xdescribeThing("The children have already left.")
children21.default_topic = "The children have already left."
square21.addThing(children21)
woman21 = Actor("woman")
woman21.ignore_if_ambiguous = True
woman21.addSynonym("baby")
woman21.setAdjectives(["woman", "with", "baby"])
woman21._verbose_name = "woman with a baby"
woman21.describeThing("")
woman21.xdescribeThing("The woman with a baby has already left the square. ")
woman21.default_topic = "The woman with a baby has already left. "
woman21.cannot_interact_msg = "The woman with a baby has already left. "
square21.addThing(woman21)
man21 = Actor("man")
man21.ignore_if_ambiguous = True
man21.addSynonym("barrow")
man21.addSynonym("fruits")
man21.addSynonym("fruit")
man21.setAdjectives(["man", "with", "barrow", "of", "fruit", "fruits"])
man21._verbose_name = "man with a barrow"
man21.describeThing("")
man21.xdescribeThing("The man with the barrow isn't here anymore.")
man21.default_topic = "The man with the barrow isn't here anymore. "
man21.cannot_interact_msg = "The man with the barrow isn't here anymore. "
square21.addThing(man21)

# HALL 22 (Hall of the Blessed)
hall22 = Room("Ornately Built Hall", "The building is large, and the ceiling, high. ")
hall22.south = square21
hall22.exit = square21
square21.north = hall22
windows22 = Thing("windows")
windows22.invItem = False
windows22.addSynonym("window")
windows22.setAdjectives(["stained", "glass", "high"])
windows22._verbose_name = "stained glass windows"
windows22.describeThing("High on the north wall, stained glass windows let in a mosaic of colorful light. ")
windows22.storm_desc = "The high stained glass window is dim in the darkness of the storm. "
windows22.storm_xdesc = "The high stained glass window is dim in the darkness of the storm. "
windows22.xdescribeThing("The stained glass windows, near the roof, depict a large group of people bowed low to the ground, as their are bathed in rays of multicoloured light. ")
hall22.addThing(windows22)
blessed22 = Actor("blessed")
blessed22._verbose_name = "Blessed"
blessed22.isDefinite = True
blessed22.addSynonym("people")
blessed22.addSynonym("seven")
blessed22.addSynonym("men")
blessed22.addSynonym("women")
blessed22.setAdjectives(["white", "robed", "seven"])
blessed22.describeThing("Sitting cross-legged in a line against the back wall are seven people, of various ages, wearing long white robes. All of them wear an identical expression of detached irritation, and all of them are staring at you. ") 
blessed22.storm_desc = "Seven people in white robes lie scattered on the floor of the Hall, faces frozen in unblinking, indentical agony. They look dead. "
blessed22.storm_desc = "Seven people in white robes lie scattered on the floor of the Hall, faces frozen in unblinking, indentical agony. They look dead. "
blessed22.xdescribeThing("As far as you can tell, the seven are made up of three men, and four women, though their identical dress, and close-shaven hair makes it difficult to discern. Most of them seem to be in their thirties, with one older, and one younger. The seven cock their heads in unison, narrowing their eyes as you stare at them. ")
blessed_default = Topic(f"\"You are not of this land,\" chorus the white robed people, their voices flat. They move in perfect unison. \"The Heretic has protected you for now, but her power is nothing compared to Ours. You will give yourself to Our Goddess, or you will die. Do not waste Our time.\"")
def blessed_default_func(game):
    goddess_abs.makeKnown(me)
    goddess_abs.level=1
    blessed22.printSuggestions(game)
    game.addText(blessed_default.text)
blessed_default.func = blessed_default
blessed_crystal = Topic(f"\"We do not care about your foreign technology,\" says the youngest. The others join in as she continues. \"We have tolerated you so far, but you will not last long if you disturb Our peace. We see through many sets of eyes. We can strike you down in an instant. Do not forget it.\"")
blessed_crystal_special = SpecialTopic("ask about your power crystal", blessed_crystal.text)
blessed22.addTopic("asktell", blessed_crystal, boat_power)
blessed_crystal_special.addAlternatePhrasing("ask them blessed about the my your power crystal")
blessed22.default_topic = blessed_default.text
hall22.addThing(blessed22)

# TOWER 23 (Watchtower)
tower23 = Room("Watchtower", "The room inside the watchtower is small, lit by two torches. ")
tower23.north = square21
tower23.exit = square21
square21.south = tower23
tower23.east_wall.xdescribeThing("On the east wall is a torch in a fixture. ")
tower23.west_wall.xdescribeThing("On the west wall is a torch in a fixture. ")
desk23 = Thing("desk")
desk23.invItem = False
desk23.setAdjectives(["rough", "wood", "wooden"])
desk23._verbose_name = "wooden desk"
desk23.describeThing("")
desk23.xdescribeThing("The desk, made of rough wood, is heaped with papers. ")
tower23.addThing(desk23)
def tower_desk_set(game, dobj):
	game.addText(f"\"Hey!\" the guard snaps. \"This is my office, not yours.\"<br> You withdraw your hand. ")
	return False
desk23.setOnVerbIobj = tower_desk_set
torches23 = Thing("torches")
torches23.invItem = False
torches23.cannotTakeMsg = "You probably shouldn't try to steal a torch from the town guard. If you need a light source, use the light crystal from your boat. "
torches23.addSynonym("torch")
torches23.addSynonym("fixtures")
torches23.addSynonym("fixtures")
torches23.describeThing("Two torches light the room from fixtures on opposite walls. ")
torches23.xdescribeThing("Two torches light the room from fixtures on opposite walls. ")
tower23.addThing(torches23)
guard23 = Actor("guard")
guard23.addSynonym("villager")
guard23.describeThing("A tired looking guard glares at you from behind a wooden desk. ")
guard23.storm_desc = "A lone guard is slumped dead in a corner. "
guard23.storm_xdesc = "A lone guard is slumped dead in a corner. "
guard23.xdescribeThing("The guard wears a peaked cap over his dark hair. He narrows his eyes as you stare at him. ")
meet_guard = Topic("The guard looks up at you. \"You must be Arai's pet foreigner. That fool woman will come to no good end. I would have let you die, had I found you. The Goddess needs to eat.\"")
guard23.setHiTopics(meet_guard, None)
guard23.default_topic = "The guard scowls at you. \"Don't bother me.\""
guard_hermit = Topic("The guard is dead. ")
guard23.storm_hermit_topic = guard_hermit
tower23.addThing(guard23)

# ROAD 24 (Cobblestone Road, North Bend)
road24 = OutdoorRoom("Cobblestone Road, North Bend", "A cobblestone road leads north, and west. ")
road24.ceiling.xdescribeThing(f"{skyState()}")
road24.west = square21
square21.east = road24
road24.sw_false_msg = "You cannot go that way. The road leads north and west. There is a hall to the south, and a shipyard to the east. "
road24.ne_false_msg = "You cannot go that way. The road leads north and west. There is a hall to the south, and a shipyard to the east. "
road24.e_false_msg = "You cannot go that way. The road leads north and west. There is a hall to the south, and a shipyard to the east. "
road24.nw_false_msg = "You cannot go that way. The road leads north and west. There is a hall to the south, and a shipyard to the east. "
road24.se_false_msg = "There is only farmland to the southeast. The road leads north and west. There is a hall to the south, and a shipyard to the east. "
road24.floor.addSynonym("road")
road24.floor.addSynonym("cobblestones")
road24.floor.setAdjectives(["cobblestone"])
road24.floor.xdescribeThing("The road is made of cobblestones. ")
road24.floor.describeThing("")
farmThing24 = farmThing18.copyThingUniqueIx()
road24.addThing(farmThing24)
road24.addThing(townThing18)
shipyardThing24 = Thing("shipyard")
shipyardThing24.addSynonym("yard")
shipyardThing24.setAdjectives(["ship"])
shipyardThing24._verbose_name = "shipyard"
shipyardThing24.invItem = False
shipyardThing24.describeThing("To the east is a shipyard. ")
shipyardThing24.xdescribeThing("To the east is a shipyard. ")
road24.addThing(shipyardThing24)
def go_in_shipyard(game):
	import intficpy.travel as travel
	travel.travelE(game)
shipyardThing24.climbInVerbDobj = go_in_shipyard
hallThing24 = Thing("hall")
hallThing24.addSynonym("building")
hallThing24.setAdjectives(["small", "well", "maintained"])
hallThing24.invItem = False
hallThing24.describeThing("To the south is a hall, smaller and less decorated than the one in Town Square, but still well maintained. ")
hallThing24.xdescribeThing("To the south is a hall, smaller and less decorated than the one in Town Square, but still well maintained. ")
road24.addThing(hallThing24)
def go_in_hall24(game):
	import intficpy.travel as travel
	travel.travelS(game)
hallThing24.climbInVerbDobj = go_in_hall24

# HALL 25 (Hall of Endings)
hall25 = Room("Hospital", "Inside is a long hall, with white walls. This appears to be a hospital. ")
hall25.north = road24
hall25.exit = road24
road24.south = hall25
beds25 = Thing("beds")
beds25.addSynonym("bed")
beds25.invItem = False
beds25.describeThing("Along the wall is a row of perhaps twenty beds. In each bed, a person lies staring at the ceiling above, unmoving. Most are old, but not all. There are even a few children. There are a lot of people here, considering how small the village is. A woman in grey, perhaps a nurse, walks back and forth along the line of beds, occasionally stopping to adjust a blanket or pillow. She pauses to look up at you for a moment before returning to her work. ")
beds25.storm_desc = "Along the wall is a row of perhaps twenty beds. All of the occupants appear to be dead. "
hall25.addThing(beds25)
patients25 = Actor("patients")
patients25.addSynonym("people")
patients25.addSynonym("person")
patients25.addSynonym("patient")
patients25.addSynonym("children")
patients25.describeThing("")
patients25.xdescribeThing("The people in the beds stare up at the ceiling, breathing, and blinking, but otherwise never stirring. ")
patients25.storm_xdesc = "All of these people appear dead. "
hall25.addThing(patients25)
nurse25 = Actor("nurse")
nurse25.addSynonym("woman")
nurse25.addSynonym("grey")
nurse25.addSynonym("gray")
nurse25.setAdjectives(["woman", "in"])
nurse25._verbose_name = "nurse"
nurse25.describeThing("")
nurse25.storm_desc = "The nurse lies on the ground, curled in a ball, her face wet from tears, but blank. Her eyes drift to look at you, but you don't think she really sees you. "
nurse25.storm_xdesc = "The nurse lies on the ground, curled in a ball, her face wet from tears, but blank. Her eyes drift to look at you, but you don't think she really sees you. "
nurse25.xdescribeThing("The nurse is a young woman, with short brown hair. ")
hall25.addThing(nurse25)
nurse_hi = Topic(f"\"Oh! Hello,\" says the nurse. \"You must be the foreigner I've heard about. You were staying in Arai's shack, by the shore, right? I hope Arai's treating you all right. She means well, but she's not quite right. Doubtless you've noticed. Just be careful.\"")
nurse25.default_topic = f"\"Hello,\" says the nurse. \"Did you need something?\""
nurse25.setHiTopics(nurse_hi, None)
nurse_knows_arai = SpecialTopic("ask if she knows Arai well", "The nurse sighs. \"I used to know her,\" she says. \"We used to be very close. About six years ago, she started acting strangely. She was saying all manner of bizarre things - that we were all being mind controlled, that the Goddess was sapping our life, that the Blessed were out to get her. She stopped praying with us. She stopped drinking with us. For a long time, I kept trying to convince her, to guide her back to the Goddess. Eventually, with all that time spent listening to her ravings, I started to believe what Arai was saying. I nearly died, acting on her advice. She meant well - she's not a bad person - but she's not a safe person, either. She moved out of the village, after that. I haven't spoken to her since.\"")
nurse_arai = Topic(nurse_knows_arai.text)
nurse_knows_arai.addAlternatePhrasing("ask do you know arai well")
nurse25.addSpecialTopic(nurse_knows_arai)
nurse25.addTopic("asktell", nurse_arai, arai)
nurse_knows_arai = SpecialTopic("ask if she knows Arai well", "The nurse sighs. \"I used to know her,\" she says. \"We used to be very close. About six years ago, she started acting strangely. She was saying all manner of bizarre things - that we were all being mind controlled, that the Goddess was sapping our life, that the Blessed were out to get her. She stopped praying with us. She stopped drinking with us. For a long time, I kept trying to convince her, to guide her back to the Goddess. Eventually, with all that time spent listening to her ravings, I started to believe what Arai was saying. I nearly died, acting on her advice. She meant well - she's not a bad person - but she's not a safe person, either. She moved out of the village, after that. I haven't spoken to her since.\"")
nurse_leave_island = SpecialTopic("ask about travel to and from the island", f"\"Nobody leaves,\" the nurse says. \"But those of us whom the Goddess protects can sail safely in the waters around the island. The Goddess will protect you, too, if you give yourself to Her. You'll be safe then.\"")
nurse25.addSpecialTopic(nurse_leave_island)
nurse_hermit = Topic("The nurse does not respond. ")
nurse25.storm_hermit_topic = nurse_hermit

# YARD 26 (Shipyard)
yard26 = OutdoorRoom("Shipyard", "A path leads through the shipyard, from town to the west, to the harbour to the northeast. ")
tani_arrive_cut = False
def yard26Arrive(game):
	global tani_arrive_cut
	if daughter.location==yard26 and not tani_arrive_cut:
		daughter.can_lead = False
		daughter.default_topic = daughter_default3
		boatmaker.defaultTopic = boatmakerDefault2
		boatmaker.removeAllSpecialTopics()
		boatmaker.removeAllTopics()
		daughter.removeAllSpecialTopics()
		daughter.removeAllTopics()
		boatmaker.describeThing("The boatmaker sits by the fence, reading a schematic. His daughter Tani leans on his shoulder. ")
		daughter.describeThing("")
		#yard26.removeThing(boatmaker)
		#yard26.removeThing(daughter)
		game.addText(f"{boatmaker.capNameArticle(True)} runs out to meet you as you enter the shipyard. His daughter throws herself into his arms. <br> \"Tani!\" he cries. \"You've come back to me!\" <br> \"The Outsider helped me find my way,\" Tani says. \"I'd lost the path. I slipped on some loose rocks as I was walking through the mountains.\"<br> \"Lost the path!\" the boatmaker cries. \"What a cruel fate! Thank the Goddess you were found. The Outsider must have the same ability as Arai - to navigate even when off the path. How strange.\" He turns to you. \"Thank you for rescuing my daughter, Noble Outsider. I heard your boat was damaged by the Storm. Please, take this. It's the least I can do.\"")
		game.addText("(Received: patch kit)")
		me.addThing(patchkit)
		tani_arrive_cut = True
yard26.arriveFunc = yard26Arrive
yard26.ceiling.xdescribeThing(f"{skyState()}")
yard26.west = road24
road24.east = yard26
yard26.s_false_msg = "There is only farmland to the south. The path leads west and northeast. "
yard26.se_false_msg = "There is only farmland to the southeast. The path leads west and northeast. "
yard26.sw_false_msg = "There is only farmland to the southwest. The path leads west and northeast. "
yard26.n_false_msg = "A fence blocks the way. The path leads west and northeast. "
yard26.nw_false_msg = "A fence blocks the way. The path leads west and northeast. "
yard26.e_false_msg = "A fence blocks the way. The path leads west and northeast. "
ship26 = Thing("ship")
ship26.invItem = False
ship26.addSynonym("construction")
ship26.setAdjectives(["large", "ship", "under"])
ship26._verbose_name = "ship under construction"
yard26.addThing(ship26)
ship26.describeThing("On the north side of the yard, a large ship is under construction. ")
ship26.xdescribeThing("On the north side of the yard, a large ship is under construction. ")
boatmaker = Actor("boatmaker")
boatmaker.addSynonym("man")
boatmaker.addSynonym("shipbuilder")
boatmaker.addSynonym("maker")
boatmaker.addSynonym("builder")
boatmaker.setAdjectives(["middle", "aged", "boat", "ship"])
boatmaker._verbose_name = "boatmaker"
boatmaker.describeThing("A middle aged man leans on the fence near the ship his brow furrowed. He is looking down at the schematic in his hands. Every few seconds, he glances up, with a look of anxious hope, then back down at the schematic, forlorn.")
boatmaker.storm_desc = ""
boatmaker.storm_xdesc = "The boatmaker's chest rises and falls, but he doesn't make a move to comfort his distraught daughter. "
daughter.storm_desc = "The boat maker lies on the ground, half in a puddle. His shivering daughter kneels beside him. She shakes his shoulder, tearful. "
boatmaker.storm_hermit_state = Topic(f"\"The boatmaker gets an abstracted look on his face for a moment, but he doesn't answer you. ")
daughter.storm_hermit_state = Topic(f"\"Papa,\" she says, between sobs. \"Papa, please.\" You're not sure she can hear you. ")
boatmaker.xdescribeThing(f"{boatmaker.capNameArticle(True)} is tall and strong, with greying black hair. His face has the beginnings of wrinkles. ")
def lostDaughterDefault(app, suggest=True):
	game.addText(f"\"Sorry,\" says {boatmaker.lowNameArticle(True)} . \"I'm a little distracted. My daughter is missing.\"")
	boatmaker.addSpecialTopic(boatmaker_daughter_special)
	boatmaker.printSuggestions(game)
boatmaker.defaultTopic = lostDaughterDefault
boatmaker_daughter = Topic(f"\"My daughter didn't come home last night,\" says {boatmaker.lowNameArticle(True)} . \"She was walking in the woods. I'm terrified something's happened to her. Her name is Tani. She's seventeen years old and tall, with short black hair. Yesterday, she was wearing a light green dress. Please, if you see her, bring her home.\"")
def boatmakerDaughter(app, suggest=True):
	game.addText(boatmaker_daughter.text)
	##hints.setNode(findDaughterHintNode)
	#hints.closeNode(talkBoatmakerHintNode)
	daughter.addSpecialTopic(daughter_father)
	if daughter.ix in me.knows_about:
		boatmaker.addSpecialTopic(boatmaker_daughter2_special)
	boatmaker.printSuggestions(game)
boatmaker_daughter_special = SpecialTopic("ask about his missing daughter", boatmaker_daughter.text)
boatmaker_daughter_special.func = boatmakerDaughter
boatmaker_daughter2_special = SpecialTopic("tell him you've found his daughter", f"\"What?\" {boatmaker.lowNameArticle(True)} cries in horror. \"She's off the path? And you came back without her? Please, Outsider, don't be so cruel. You appear to have the power to move without Her guidance, but we do not. Tani will die out there if you don't go back for her. I'll reward you! I'll be forever in your debt! Just bring my daughter home.\"")
yard26.addThing(boatmaker)
schematic26 = Thing("schematic")
schematic26.invItem = False
schematic26.cannotTakeMsg = "It wouldn't be polite to grab the schematic from the shipbuilder's hands. You don't need it anyway. "
schematic26.describeThing("")
schematic26.xdescribeThing("The shipbuilder is reading a schematic. ")
yard26.addThing(schematic26)
fence26 = Thing("fence")
fence26.setAdjectives(["wooden"])
fence26.invItem = False
fence26.describeThing("")
fence26.xdescribeThing("A wooden fence encircles the shipyard. ")
yard26.addThing(fence26)

# ROAD 27 (Cobblestone Road, End)
road27  = OutdoorRoom("Cobblestone Road, End", "The cobblestone road ends here. Dirt paths lead north, into the forest, east, toward shore, and south, back toward the town. ")
road27.storm_desc = "The cobblestone road ends here. The dirt paths that lead north and east have become rivers of mud. "
road27.ceiling.xdescribeThing(f"{skyState()}")
road27.south = road24
road24.north = road27

road27.nw_false_msg = "The forest is too thick to the northwest. You can follow the road south, or take one of the smaller paths leading north or east. You can also go northeast, to the scrapyard. "
road27.w_false_msg = "You cannot go west from here. You can follow the road south, or take one of the smaller paths leading north or east. You can also go northeast, to the scrapyard. "
road27.sw_false_msg = "You cannot go southwest from here. You can follow the road south, or take one of the smaller paths leading north or east. You can also go northeast, to the scrapyard. "
road27.se_false_msg = "The way southeast is blocked by the shipyard fence. You can follow the road south, or take one of the smaller paths leading north or east. You can also go northeast, to the scrapyard. "
road27.n_msg = "You follow the path through the forest, until you arrive at a stone-paved clearing. "

copper2 = copper1.copyThing()
road27.addThing(copper2)

forestThing27 = forestThing2.copyThingUniqueIx()
forestThing27.setAdjectives(["north", "forest"])
forestThing27.addSynonym("path")
forestThing27._verbose_name = "forest path"
forestThing27.xdescribeThing("A wide path leads north through the trees. ")
forestThing27.describeThing("")
def go_in_forest27(game):
	import intficpy.travel as travel
	travel.travelN(game)
forestThing27.climbInVerbDobj = go_in_forest27
road27.addThing(forestThing27)
road27.removeThing(road27.floor)
road27.floor.setFromPrototype(road24.floor)
road27.addThing(road27.floor)
scrapyardThing27 = Thing("scrapyard")
scrapyardThing27.addSynonym("yard")
scrapyardThing27.addSynonym("junkyard")
scrapyardThing27.setAdjectives(["scrap", "junk"])
scrapyardThing27._verbose_name = "scrapyard"
scrapyardThing27.invItem = False
scrapyardThing27.describeThing("Just northeast of the path is the entrance to a scrapyard. ")
scrapyardThing27.xdescribeThing("Just northeast of the path is the entrance to a scrapyard ")
road27.addThing(scrapyardThing27)
def go_in_scrapyard(game):
	import intficpy.travel as travel
	travel.travelNE(game)
scrapyardThing27.climbInVerbDobj = go_in_scrapyard

# YARD 28 (Scrapyard)
yard28 = OutdoorRoom("Scrapyard", "A path leads through the scrapyard, from  southwest to east. ")
yard28.ceiling.xdescribeThing(f"{skyState()}")
yard28.southwest = road27
road27.northeast = yard28
yard28.s_false_msg = "A fence blocks the way to the south. The path leads east, southwest and southeast. "
yard28.n_false_msg = "A fence blocks the way to the north. The path leads east, southwest and southeast. "
yard28.w_false_msg = "A fence blocks the way to the west. The path leads east, southwest and southeast. "
yard28.ne_false_msg = "A fence blocks the way to the northeast. The path leads east, southwest and southeast. "
yard28.nw_false_msg = "A fence blocks the way to the northwest. The path leads east, southwest and southeast. "
scrap28 = Thing("scrap")
scrap28.invItem = False
scrap28.addSynonym("pile")
scrap28.addSynonym("piles")
scrap28.addSynonym("parts")
scrap28.addSynonym("boats")
scrap28.setAdjectives(["pile", "piles", "of", "scrap", "broken", "boat", "parts", "from"])
scrap28._verbose_name = "piles of scrap"
scrap28.cannotTakeMsg = "You don't need broken boat parts. "
yard28.addThing(scrap28)
scrap28.describeThing("On both sides of the path, scrap is piled as high as your head. There are thousands of broken boat parts here, some barely recognizable. ")
scrap28.storm_desc = "The wind has scattered the piles of scrap across the entire yard. "
scrap28.storm_xdesc = "The wind has scattered the piles of scrap across the entire yard. "
scrap28.xdescribeThing("Piles of scrap, some as high as your head, fill the yard. There are thousands of broken boat parts here, some barely recognizable. ")
picker = Actor("picker")
picker.storm_desc = "Ket the Picker sits alone at a table, eyes wide, in a look of dazed terror. She stares at the empty Kaur cup in her hands. "
picker.storm_hermit_state = Topic(f"\"I can't feel Her,\" says Ket. \"I can't feel her at all. I'm alone. I've never been so alone in my life. If she will not keep me as Her child, let me die in Her Storm.\" ")
picker.addSynonym("woman")
picker.addSynonym("ket")
picker.setAdjectives(["young", "wreck", "scrapyard", "scrap", "yard"])
picker._verbose_name = "picker"
picker.describeThing("A young woman crouches by a small pile, carefully sorting through the parts. On the ground beside her is a shovel. Behind her, a wooden fence surrounds the yard. ")
picker.xdescribeThing("The young woman wears rough leather gloves. Short-cropped red hair sticks out from under her battered helmet. ")
picker.tavern_bound = False
picker_hi1 = Topic(f"\"Hello,\" says {picker.lowNameArticle(True)} . \"You must be the outsider Arai saved. She really went out on a limb for you - turning her magic against the Storm, and sheltering you in her own home. It's surprising really, considering how little she does for her <i>own</i> community. I'm Ket, by the way. I own the scrapyard here. I salvage parts from the ships that crash on our shores. It's good to meet you.\" ")
def pickerHiFunc1(app, suggest=True):
	game.addText(picker_hi1.text)
	if suggest:
		picker.printSuggestions(game)
	picker.makeProper("Ket the Picker")
	if not arai.has_proper_name:
		arai.makeProper("Arai, the woman from the shack")
		arai.removeSynonym("shack")
picker_hi1.func = pickerHiFunc1
picker_hi1.owner = picker
picker_hi2 = Topic(f"\"Hello again,\" says {picker.lowNameArticle(True)} . \"What can I do for you?\" ")
picker.setHiTopics(picker_hi1, picker_hi2)
def pickerDefault(app, suggest=True):
	game.addText(f"{picker.capNameArticle(True)} looks at you in confusion. ")
	if suggest:
		picker.printSuggestions(game)
picker.defaultTopic = pickerDefault
scrap_topic = Topic(f"{picker.capNameArticle(True)} smiles proudly. \"I gathered all this myself, from ships that have crashed on our shores. Impressive, isn't it?\" ")
picker.addTopic("asktell", scrap_topic, scrap28)
myboat_picker = Topic(f"\"Ah, yes,\" says {picker.lowNameArticle(True)} . \"I was just over there this morning.\"")
picker.addTopic("asktell", myboat_picker, myboat)
picker_compass = Topic(f"\"Yes, I took it,\" says {picker.lowNameArticle(True)} . \"I'm sorry, but I won't give it back. If you have a compass, you'll try to sail away, and the Goddess of the Storm will kill you. I don't want to breed ill will between us. Why don't you come for a drink with me? I'd be happy to answer any questions you have about our island, and our Goddess.\" ")
picker.addTopic("asktell", picker_compass, mycompass)
picker_hermit1 = Topic(f"\"I'll meet you at the tavern,\" says {picker.lowNameArticle(True)} . \"I just gotta finish up here.\" ")
def pickerCompass(game):
	game.addText(picker_compass.text)
	picker.tavern_bound = True
	removeCompassTopics()
	arai.location.removeThing(arai)
	market19.addThing(arai)
	picker.setHermitTopic(picker_hermit1)
	arai.setHermitTopic(arai_warning2)
	goddess_abs.makeKnown(me)
	goddess_abs.level = 1
	##hints.setNode(meetKetHintNode)
	#hints.closeNode(talkPickerHintNode)
	if storm_abs.known_ix in me.knows_about:
		me.knows_about.remove(storm_abs.known_ix)
	arai.describeThing(f"{arai.capNameArticle(False)} stands in the south of the square, near the entrance to the wooden building. She watches you as you move through the market. ")
	market19.descFunc = araiWarning1
picker_compass.func = pickerCompass
picker_compass_special = SpecialTopic("ask if she's seen your compass", picker_compass.text)
picker_compass_special.addAlternatePhrasing("ask her picker if she's seen my your compass")
picker_compass_special.addAlternatePhrasing("have you seen my compass")
picker_compass_special.func = pickerCompass
picker_sail = Topic(f"\"Yeah, I noticed the sail was torn. It didn't look too bad. You can probably just sew it up,\" says {picker.lowNameArticle(True)} . \"Not that I'd recommend trying to set sail from here, outsider that you are.\" ")
picker.addTopic("asktell", picker_sail, boat_sail)
picker_sail_special = SpecialTopic("ask about repairing torn sails", picker_sail.text)
picker_sail_special.addAlternatePhrasing("ask her picker about repairing my your torn sail")
def pickerSail(app, suggest=True):
	#hints.setNode(talkVendorHintNode)
	game.addText(picker_sail_special.text)
	if suggest:
		picker.printSuggestions(game)
picker_sail.func = pickerSail
picker_sail_special.func = pickerSail
picker_hull = Topic(f"\"The hull didn't seem beyond repair when I saw it this morning. Just patch it,\" says {picker.lowNameArticle(True)} . \"That being said, you should consider staying here.\" ")
picker.addTopic("asktell", picker_hull, myboat)
picker_hull_special = SpecialTopic("ask about patching holes in boats", picker_hull.text)
picker_hull_special.addAlternatePhrasing("ask her picker about patching repairing fixing my your boat hull")
def pickerHull(app, suggest=True):
	#hints.setNode(talkBoatmakerHintNode)
	game.addText(picker_hull_special.text)
	if suggest:
		picker.printSuggestions(game)
picker_hull.func = pickerHull
picker_hull_special.func = pickerHull
picker_crystal = Topic(f"\"Oh! That weird crystal thing is a power source?\" says {picker.lowNameArticle(True)} . \"Sorry. I don't know anything about it. It might not be such a bad thing that it's broken, though. It wouldn't be a good idea to try and sail away from here.\" ")
picker.addTopic("asktellgiveshow", picker_crystal, boat_power)
picker_crystal_special = SpecialTopic("ask about power crystals", picker_crystal.text)
picker_crystal_special.addAlternatePhrasing("ask her picker ket woman about repairing fixing my your power crystal crystals source")

picker_hi3 = Topic(f"\"You came!\" says Ket. \"I'm so glad. As promised, I'll tell you all about the island. Have some Kaur.\" Ket beams. ")
def pickerHi3(app, suggest=True):
	game.addText(picker_hi3.text)
	picker.addSpecialTopic(picker_kaur_special)
	picker.addSpecialTopic(picker_accept_kaur)
	##hints.setNode(findWreckHintNode)
	#hints.closeNode(meetKetHintNode)
	if suggest:
		picker.printSuggestions(game)
picker_hi3.func = pickerHi3
picker_hi4 = Topic(f"\"Hey,\" says Ket. \"You haven't had any Kaur! Drink some, won't you? You'll be safe from the Storm if you do.\"")
picker_kaur = Topic(f"\"Kaur is a gift of the Goddess,\" says Ket. She takes a swig of her drink, and continues. \"It helps us to connect to her. She protects everyone who drinks it. She'll protect you, too, if you have some. You will, won't you?\"")
picker_kaur_special = SpecialTopic("ask about the drink called Kaur", picker_kaur.text)
def pickerKaur(app, suggest=True):
	game.addText(picker_kaur.text)
	picker.removeSpecialTopic(picker_kaur_special)
	picker.addSpecialTopic(picker_goddess_special)
	picker.printSuggestions(game)
picker_kaur.func = pickerKaur
picker_kaur_special.func = pickerKaur
picker_goddess = Topic(f"\"The Goddess of the Storm is fearsome,\" says Ket. \"She kills every outsider who passes through our waters. She would have killed you, too, if it weren't for Arai's enchantment. She might yet, if you don't drink up. To we, her devoted, the Goddess is a protector; a mother. At the four altars, we kneel and pray. We drink of the Kaur. In return, we have peace, and prosperity. It's not such a bad trade. Join us, won't you? Have some Kaur.\" ")
picker_goddess_special = SpecialTopic("ask about the Goddess of the Storm", picker_goddess.text)
def pickerGoddess(app, suggest=True):
	game.addText(picker_goddess.text)
	picker.removeSpecialTopic(picker_goddess_special)
	altar_n29.makeKnown(me)
	picker.addSpecialTopic(picker_altars_special)
	picker.printSuggestions(game)
picker_goddess.func = pickerGoddess
picker_goddess_special.func = pickerGoddess
picker_altars = Topic("Ket sips on her drink. \"At the temple, there are four altars to the Storm - the north, the south, the east, and the west,\" she says. \"Each altar corresponds to an element of life. Its meaning is encapsulated in a symbol. The north altar is Earth. It's about the material world, in particular, our wealth, and posessions. Its symbol is the Disk. The east altar is Air - conflict, internal and external. Its symbol is the Wing. The south is Fire. It's about energy, and creativity. The truest Fire is the power of the Sun itself. Finally, the west, Water, is about emotions and relationships. That one's the Ocean. <br>\"When we need help from our Goddess, we pray in the temple. Sometimes, we make an offering - usually just Kaur - at the altar that corresponds to our problem. Speaking of Kaur, aren't you going to have some?\" ")
picker_altars_special = SpecialTopic("ask about the four altars", picker_altars.text)
def pickerAltars(app, suggest=True):
	game.addText(picker_altars.text)
	#picker.removeSpecialTopic(picker_altars_special)
	picker.addSpecialTopic(kaur_offering_topic)
	picker.printSuggestions(game)
picker_altars.func = pickerAltars
picker_altars_special.func = pickerAltars
picker_accept_kaur = SpecialTopic("accept the Kaur", "You accept the Kaur Ket offers you. <br>The liquid in the cup is thick and green. It smells like fermented fruit, with a hint of something chemical. You take a sip. Instantly, you feel at ease. You smile at Ket, and she smiles back. Encouraged, you swallow the rest. <br>You feel Ket relax, relieved at your assured safety. You feel the others in the pub, blissful with Kaur. You feel the people of the island, moving through their many, connected lives. The Goddess of the Storm watches over Her children. She watches over <i>you.</i> You belong here, with Her. You are at peace. ")
def pickerAcceptKaur(app, suggest=True):
	game.addText(picker_accept_kaur.text)
	global special_box_style
	
	kaur_ending.endGame(game)
picker_accept_kaur.func = pickerAcceptKaur

yard28.addThing(picker)
yard28.addThing(shovel)
shovel.describeThing("")
shovel.invItem = False
shovel.cannotTakeMsg = f"{picker.capNameArticle(True)} will notice if you take her shovel. "

fence28 = Thing("fence")
fence28.setAdjectives(["wooden"])
fence28.invItem = False
fence28.describeThing("")
fence28.xdescribeThing("A wooden fence encircles the scrapyard. ")
yard28.addThing(fence28)

# TEMPLE 29 (Open Air Temple)
temple29 = OutdoorRoom("Open Air Temple ", "A large, flat circle has been paved into the ground here in polished white stones. Light, filtered by the forest canopy above, dances across them as the leaves blow in the wind. ")
temple29.storm_desc = "The wind roars through the forest around the temple. "
temple29.ceiling.xdescribeThing(f"{skyState()}")
temple29.south = road27
road27.north = temple29
temple29.n_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.ne_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.se_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.sw_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.w_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.nw_false_msg = "The forest is thick in that direction. You can return to town to the south. "
temple29.s_msg = "You follow the path south, back to the village. "
temple29.floor.addSynonym("stones")
temple29.floor.addSynonym(f"loor")
temple29.floor.setAdjectives(["polished", "white", "stone"])
temple29.floor._verbose_name = "white stone floor"
temple29.floor.describeThing("")
temple29.floor.xdescribeThing("The ground is paved in polished white stones. ")
lantern = LightSource("lantern")
lantern.setAdjectives(["brass"])
lantern.is_lit = True
lantern.player_can_extinguish = False
lantern.cannot_extinguish_msg = "If you put out the lantern, you'd have no way to light it again. "
# lantern.describeThing("There is a lantern here. ")
lantern.xdescribeThing("The lantern is made of brass. ")
lantern.invItem= False
lantern.cannotTakeMsg = "You don't need a lantern right now. Your light crystal will light your way just fine. "
lantern_stand = Surface("stand")
def putOnStandFunc(game, dobj):
	if dobj==lantern:
		game.addText("You set the lantern back on the stand. ")
		me.removeThing(lantern)
		lantern_stand.addThing(lantern)
		return False
	else:
		game.addText(dobj.capNameArticle(True) + " doesn't fit on the stand. ")
		return False
lantern_stand.setInVerbIobj = putOnStandFunc
lantern_stand.setAdjectives(["lantern"])
lantern_stand.invItem = False
temple29.addThing(lantern_stand)
lantern_stand.addThing(lantern)
lantern_stand.describeThing("Near the entrance to the temple is a lantern stand. ")
lantern_stand.xdescribeThing("Near the entrance to the temple is a lantern stand. ")
altar_n29 = Surface("altar")
altar_n29.addSynonym("altars")
altar_n29.cannotTakeMsg = "The stone altar is too heavy to move" 
altar_n29.desc_reveal = False
altar_n29.setAdjectives(["north", "stone"])
altar_n29._verbose_name = "north altar"
altar_n29.describeThing("Four stone altars stand on the edge of the circle, to the north, south, east, and west. ")
altar_n29.xdescribeThing("The north altar is made of smooth, white stone. ")
temple29.addThing(altar_n29)
altar_s29 = Surface("altar")
altar_s29.addSynonym("altars")
altar_s29.cannotTakeMsg = "The stone altar is too heavy to move" 
altar_s29.desc_reveal = False
altar_s29.setAdjectives(["south", "stone"])
altar_s29._verbose_name = "south altar"
altar_s29.describeThing("")
altar_s29.xdescribeThing("The south altar is made of smooth, white stone. ")
temple29.addThing(altar_s29)
def putOnAltarS(game, dobj):
	if dobj==lightcrystal:
		lantern.invItem = True
	return True
altar_s29.setOnVerbIobj = putOnAltarS
altar_e29 = Surface("altar")
altar_e29.addSynonym("altars")
altar_e29.cannotTakeMsg = "The stone altar is too heavy to move" 
altar_e29.desc_reveal = False
altar_e29.setAdjectives(["east", "stone"])
altar_e29._verbose_name = "east altar"
altar_e29.describeThing("")
altar_e29.xdescribeThing("The east altar is made of smooth, white stone. ")
temple29.addThing(altar_e29)
altar_w29 = Surface("altar")
altar_w29.addSynonym("altars")
altar_w29.cannotTakeMsg = "The stone altar is too heavy to move" 
altar_w29.desc_reveal = False
altar_w29.setAdjectives(["west", "stone"])
altar_w29._verbose_name = "west altar"
altar_w29.describeThing("")
altar_w29.xdescribeThing("The west altar is made of smooth, white stone. ")
temple29.addThing(altar_w29)
forestThing29 = forestThing14.copyThingUniqueIx()
forestThing29.describeThing("")
temple29.addThing(forestThing29)

# SHORE 30 (HARBOUR))
shore30 = OutdoorRoom("Shore, Harbour", "Along the sandy shore, docks extend out into the ocean. The beach continues to the north. To the west, a road leads into town. A path to the southwest leads to the shipyard. ")
shore30.ceiling.xdescribeThing(f"{skyState()}")
#shore30.west = road27
#road27.east = shore30
harbourpath27 = TravelConnector(road27, "e", shore30, "w", "path")
harbourpath27.entranceA.describeThing("")
harbourpath27.entranceA.setAdjectives(["east", "dirt"])
harbourpath27.entranceA._verbose_name = "east path"
harbourpath27.entranceA.describeThing("")
harbourpath27.entranceA.xdescribeThing("The path leads east, toward the shore. ")
harbourpath27.entranceA_msg = "You follow the path east. "
harbourpath27.entranceB.describeThing("")
harbourpath27.entranceB.xdescribeThing("The path leads east, toward the shore. ")
harbourpath27.entranceB_msg = "You follow the path west. "
yard26.northeast = shore30
shore30.southwest = yard26

shore30.s_false_msg = "The forest is too thick to go far in that direction. Paths lead north, west, and southwest from here. "
shore30.nw_false_msg = "The forest is too thick to go far in that direction. Paths lead north, west, and southwest from here. "
shore30.ne_false_msg = "There is only ocean to the northeast. It's probably not wise to try and cross it without a boat. Paths lead north, west, and southwest from here. "
shore30.e_false_msg = "The there is only ocean to the east. It's probably not wise to try and cross it without a boat. Paths lead north, west, and southwest from here. "
shore30.se_false_msg = "The there is only ocean to the southeast. It's probably not wise to try and cross it without a boat. Paths lead north, west, and southwest from here. "
ocean30 = ocean5.copyThingUniqueIx()
ocean30.describeThing("")
shore30.addThing(ocean30)
seawater30 = seawater2.copyThing()
ocean30.addThing(seawater30)
shore30.floor.addSynonym("sand")
shore30.floor.addSynonym("beach")
shore30.floor.xdescribeThing("The ground is sandy. Toward the east, it is damp from the waves. ")
shore30.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore30.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
forestThing30 = forestThing5.copyThingUniqueIx()
forestThing30.describeThing("A thick forest blocks travel to the south. ")
forestThing30.xdescribeThing("A thick forest blocks travel to the south. ")
shore30.addThing(forestThing30)
boats30 = Thing("boats")
boats30.addSynonym("boat")
boats30.invItem = False
boats30.cannotTakeMsg = "That would be stealing. "
boats30.describeThing("Along the docks, boats of all shapes and sizes are tied. ")
boats30.xdescribeThing("Along the docks, boats of all shapes and sizes are tied. ")
shore30.addThing(boats30)
docks30 = Thing("docks")
docks30.addSynonym("dock")
docks30.invItem = False
docks30.describeThing("")
docks30.xdescribeThing("Along the docks, boats of all shapes and sizes are tied. ")
shore30.addThing(docks30)
def go_in_boats30(game):
	game.addText("It would look pretty suspicious if you climbed into someone else's boat. ")
boats30.climbInVerbDobj = go_in_boats30
def go_on_docks30(game):
	game.addText("There's no reason to go out on the docks. ")
docks30.climbOnVerbDobj = go_on_docks30

disk = Thing("stone")
disk.setAdjectives(["flat", "round"])
disk.addSynonym("rock")
disk.addSynonym("disk")
disk.describeThing("On the ground is a flat, round stone. ")
disk.xdescribeThing("This stone is nearly a perfect disk. ")
shore30.addThing(disk)

# SHORE 31 (WRECK SITE 2)
shore31 = OutdoorRoom("Shore, Last Remnants of a Wreck", "The sandy shore continues to the south. A path to the west leads to the scrapyard. ")
shore31.ceiling.xdescribeThing(f"{skyState()}")
scrapyardpath2 = TravelConnector(shore31, "w", yard28, "e", "path")
scrapyardpath2.entranceA_msg = "You follow the path west. "
scrapyardpath2.entranceA_msg = "You follow the path east. "
scrapyardpath2.entranceA.describeThing("")
scrapyardpath2.entranceA.xdescribeThing("The path leads west. ")
scrapyardpath2.entranceB.describeThing("Another path leads east, toward shore. ")
scrapyardpath2.entranceB.xdescribeThing("The path leads east. ")
shore31.south = shore30
shore30.north = shore31
shore31.sw_false_msg = "You can go west or south from here. "
shore31.n_false_msg = "The forest is too thick to go far in that direction. You can go west or south from here. "
shore31.ne_false_msg = "There is only ocean to the northeast. You can go west or south from here. "
shore31.e_false_msg = "There is only ocean to the east. You can go west or south from here. "
shore31.se_false_msg = "There is only ocean to the southeast. You can go west or south from here."
shore31.nw_false_msg = "The forest is too thick to go far in that direction. You can go west or south from here. "
ocean31 = ocean2.copyThingUniqueIx()
ocean31.describeThing("To the east, the ocean stretches into the distance. ")
shore31.addThing(ocean31)
seawater31 = seawater2.copyThing()
ocean31.addThing(seawater31)
shore31.floor.addSynonym("sand")
shore31.floor.addSynonym("beach")
shore31.floor.xdescribeThing("The ground is sandy. Toward the east, it is damp from the waves. ")
shore31.floor.cannotTakeMsg = "You have no use for a handful of sand. "
shore31.floor.storm_xdesc = "The sand is wet, and riddled from the rain. "
forestThing31 = forestThing2.copyThingUniqueIx()
forestThing31.describeThing("To the north is a thick forest. ")
forestThing31.xdescribeThing("The trees are green, and healthy. ")
shore31.addThing(forestThing31)
wreck3 = Thing("wreck")
wreck3.addSynonym("shipwreck")
wreck3.addSynonym("boat")
wreck3.addSynonym("ship")
wreck3.setAdjectives(["last", "remnants", "of", "ruined"])
wreck3._verbose_name = "ruined ship"
wreck3.describeThing("The last remnants of a ruined ship are scattered across the shore. Anything usable has been removed. ")
wreck3.xdescribeThing("The last remnants of a ruined ship are scattered across the shore. Anything usable has been removed. ")
wreck3.invItem = False
wreck3.cannotTakeMsg = "There is nothing here worth taking. "
shore31.addThing(wreck3)

### CAVES ###
cavegroup = RoomGroup()
cavefloor = Thing("floor")
cavefloor.setAdjectives(["stone", "rock", "cave", "cavern", "solid", "sandy", "dusty"])
cavefloor.addSynonym("ground")
cavefloor.addSynonym("earth")
cavefloor.addSynonym("sand")
cavefloor.describeThing("")
cavefloor.xdescribeThing("The ground here is solid stone, covered in a thin layer of dusty sand. ")
cavefloor.cannotTakeMsg = "You have no use for a handful of dusty sand. "
cavefloor.invItem = False
cavegroup.floor = cavefloor
caveceiling = Thing("ceiling")
caveceiling.setAdjectives(["stone", "rock", "cave", "cavern", "rough"])
caveceiling.addSynonym("roof")
caveceiling.addSynonym("above")
caveceiling.describeThing("")
caveceiling.xdescribeThing("The curving cavern ceiling above you is made of rough stone. ")
caveceiling.invItem = False
cavegroup.ceiling = caveceiling

# CAVE 0 (Entrance)
cave0 = Room("Caverns, Entrance", "You are in a cavern the size of a small room. ")
def cave0arrive(game):
	#hints.closeNode(findCaveHintNode)
	pass
cave0.arriveFunc = cave0arrive
for wall in cave0.walls:
	wall.xdescribeThing("The wall is made of rough rock, curving inward toward the ceiling. ")
cave0.north_wall.describeThing("The stone wall opposite to the exit has been flattened out, and carved with images of towering ocean waves. ")
cave0.north_wall.xdescribeThing(cave0.north_wall.desc)
cave0.south = temple14
cave0.exit = temple14
temple14.north = cave0
temple14.entrance = cave0
cave0.dark = True
cave0.dark_visible_exits = ["s", "exit"]
cave0.n_msg = "You walk into the dark passageway. "
# north/down will become the entrance to the caves
cave0.n_false_msg = "The stone wall of the cavern blocks the way. "
cave0.ne_false_msg = "The stone wall of the cavern blocks the way. "
cave0.e_false_msg = "The stone wall of the cavern blocks the way. "
cave0.se_false_msg = "The stone wall of the cavern blocks the way. "
# south is out
cave0.sw_false_msg = "The stone wall of the cavern blocks the way. "
cave0.w_false_msg = "The stone wall of the cavern blocks the way. "
cave0.nw_false_msg = "The stone wall of the cavern blocks the way. "
passage0 = Thing("passageway")
passage0.setAdjectives(["dark", "north"])
passage0.invItem = False
passage0.describeThing("")
passage0.xdescribeThing("The passageway is dark. ")

def lookInPassage0(game):
	game.addText("It's too dark to see inside. ")
def putInPassage0(game, dobj):
	if dobj==lightcrystal:
		game.addText("You shine the crystal down the passageway. You still aren't able to see much. ")
	else:
		game.addText("You're not going to start dropping your possessions into dark holes. ")
	return False
def climbInPassage0(game):
	from intficpy import travel
	travel.travelN(game)
	return False
passage0.lookInVerbDobj = lookInPassage0
passage0.setInVerbIobj = putInPassage0
passage0.climbInVerbDobj = climbInPassage0

def cave0Reveal(game):
	if cave0.north:
		game.addText("Looking through the lens reveals nothing further. ")
		return True
	else:
		game.addText("The lens reveals a previously invisible passageway opening in the middle of the north wall of the cavern. ")
		cave0.north_wall.describeThing("The stone wall opposite to the exit has been flattened out, and carved with images of towering ocean waves. In the middle of the wall, a passageway leads north. ")
		cave0.north_wall.xdescribeThing(cave0.north_wall.desc)
		cave0.addThing(passage0)
		cave0.north = cave1
		cave0.enter = cave1
		return True
cave0.lensReveal = cave0Reveal
		
# CAVE 1 (Upper Level)
cave1 = Room("Caverns, Upper Level", "You are in a cavern the size of a small room. ")
def cave1Discover(game):
	arai.default_topic = arai_p2_default3
	pickaxeSuggest()
cave1.onDiscover = cave1Discover
def cave1Arrive(game):
	global storm_caves
	if storm_turns_left==storm_turns_full or storm_caves > 0:
		return None
	storm_caves += 1
	game.addText("As you enter, an image appears in your mind, vivid as the world around you. <br><br>A young man and an old man stand before you, in long brown cloaks. They are engaged in intense discussion. <br><br>\"It's something about these caves, Brother,\" the younger says. \"There's a vein of opal below us that seems to resonate with <i>something</i>. Something not of this world. If we can find a way to harness it, it could be the breakthrough we've been searching for.\"<br><br>\"Be careful, child,\" says the old man. \"Be very careful. What we do not understand, we cannot control.\"<br><br>The scene fades from your mind, leaving you once more alone in the cavern. ")
	
	return None
	#hints.closeNode(enterCaveHintNode)
cave0.arriveFunc = cave0arrive
cave1.arriveFunc = cave1Arrive
cave1.south = cave0
cave1.dark = True
#cave1.addThing(woodboard)
cave1.w_false_msg = "A large boulder blocks the way into the western cavern. "
rock1 = Thing("rock")
rock1.addSynonym("boulder")
rock1.setAdjectives(["large"])
rock1.invItem = False
rock1.cannotTakeMsg = "The rock is too heavy to move. If you want to get by, you'll have to break it somehow. "
rock1.describeThing(f"A large rock blocks the way to the west.")

rock1.xdescribeThing("The rock looks heavy. ")
def pickaxeSuggest():
	vendor.addSpecialTopic(vendor_pickaxe_special)
rock_barriers.append(rock1)
#cave1.addThing(pickaxe)
cave1.addThing(rock1)
def rock1climb(game):
	game.addText("You can't get a good enough hold on it to climb over. ")
	return False
def rock1BreakDobj(game):
	game.addText("What would you like to break it with? ")
	game.parser.command.dobj = GrammarObj(target=rock1)
	game.parser.command.verb = breakWithVerb
	game.parser.command.ambiguous = True
	return False
def rocks2BreakDobj(game):
	game.addText("What would you like to break them with? ")
	game.parser.command.dobj = GrammarObj(target=rocks1)
	game.parser.command.verb = breakWithVerb
	game.parser.command.ambiguous = True
	return False
rock1.breakVerbDobj = rock1BreakDobj
rocks2.breakVerbDobj = rocks2BreakDobj
def rock1Break(game):
	game.addText("The way west is now clear. ")
	cave1.west = cave2
rock1.crushFunc = rock1Break
pedestal1 = Thing("pedestal")
dial1 = Thing("dial")
dial1.code = ["3", "6", "15", "28"]
dial1.cur_digit = 0
dial1.describeThing("Set into the centre of the pedestal is a dial, with numbers from 0 to 30 carved into the stone around it. ")
cave1.addThing(pedestal1)
pedestal1.invItem = False
pedestal1.addComposite(dial1)
pedestal1.describeThing("In the middle of the room is a stone pedestal. ")
pedestal1.xdescribeThing("In the middle of the room is a stone pedestal. ")
# c1 -> c3 = combination 3, 6, 15, 28 (numbers between 0 and 30)

# CAVE 2 (Library)
# CAVE VISION 4/5
cave2 = Room("Study", "You are in a small cavern. ")
cave2.dark = True
cave2.east = cave1
desk2 = Surface("desk")
cave2.addThing(desk2)
chair2 = Surface("chair")
chair2.canSit = True
chair2.invItem = False
chair2.cannotTakeMsg = "The chair is too big to carry around with you. "
cave2.addThing(chair2)
vellum2 = Readable("sheet", "You read the vellum sheet. <br><br><i>I have spent many years in these caverns, with the brothers of the order. Day after day, I have studied and meditated here, in the passageway through which She entered this world. The visions do not come to me so often as they once did, but I can still feel it. Though She cannot enter this place by Her own will, Her domain being the Sky, the echoes of Her arrival still ring loud inside this stony hell. The moments leading up to that fateful instant were etched into the walls, burned into the floor, imprinted upon the soul of this place by the force of Her arrival. <br><br>We brought Her here. We allowed Her into our world - into our bodies and souls - and She has taken us for Her own. <br><br>Yes, we whom the Storm protects belong to Her. We prosper as her power grows, as she expands to take more of the world. One day, She will take everything, and we Her children will be the only humans left. This is our only choice, if we wish to live, for she kills those she does not own. This is our only choice, because, by the bond we share with the Storm, we will die if she is removed from this world. <br><br>This morning, I took the stone that my order protects - the opal that is Her connection to this world. I brought it down to the depths of these caverns, and, Heaven forgive me, I placed it in the Earth. I felt the life begin to drain out of me. I heard, from up above, screams such as I had never heard. I pulled the opal from the ground at once, but it was too late. In the seconds that they were deprived of Her strength, seven died. Ten, some as young as twelve years old, succumbed to the catatonia we call the Blessed Peace. Half of this year's crop is gone. <br><br>My brothers and I have decided to end the Order. The caverns will be abandoned, laden with traps and curses, and hidden behind a charm of concealment. The studies of magic, esotericism, and theosophy on this island will be ceased. I, for my part, will pray to be given the Blessed Peace. <br><br>Let my life be a warning to any who seek to banish the Goddess of the Storm: Her power is great, and Her reach is far. Her Connection will kill everyone it holds.</i>")
vellum2.addSynonym("vellum")
vellum2.setAdjectives(["vellum"])
vellum2.describeThing("There is a sheet of vellum here, on which someone has written in black ink. ")
vellum2.xdescribeThing("The vellum is old, but has held up remarkably well. It is covered in black writing. ")
def vellumRead(game):
	global arai_death_topics
	game.addText(vellum2.read_desc)
	if not arai_death_topics:
		arai_death_topics = True
		arai.addSpecialTopic(arai_p2_vellum1)
		arai.addSpecialTopic(arai_p2_vellum2)
vellum2.readText = vellumRead
desk2.addThing(vellum2)

# CAVE 3 (Small Cavern, contains key to Lower Level)
# CAVE VISON 2
cave3 = Room("Caverns, Upper Level East", "You are in a small cavern. ")
def cave3Arrive(game):
	#hints.setNode(l2keyHintNode)
	pass
cave3.arriveFunc = cave3Arrive
cave3.dark = True
c3door = DoorConnector(cave3, "w", cave1, "e")
c3lock = Lock(True, None)
c3door.setLock(c3lock)
l2key = Key()
l2key.setAdjectives(["large", "grey"])
cave3.addThing(l2key)
### LOWER LEVEL ###
# CAVE 4 (Lower Level, contains gold ingot)
# CAVE 4_2 (chasm)
cave4_2 = Room("Behind the Door, on the Precipice of a Chasm ", "You are on a narrow section of ground, at the edge of deep chasm stretching the width of the cavern. You can see the ground on the other side of the chasm, to the south. ")
def chasmDiscover(game):
	boatmaker.addSpecialTopic(boatmaker_board_special)
cave4_2.onDiscover = chasmDiscover
cave4_2.dark = True
chasm4_2 = Thing("chasm")
chasm4_2.invItem = False
chasm4_2.setAdjectives(["deep", "wide"])
chasm4_2.describeThing("")
chasm4_2.xdescribeThing("The chasm is deep, and wide. ")
chasm4_2.size = 100
#cave4_2.addThing(woodboard)
cave4_2.addThing(chasm4_2)
def chasmSetIn(game, dobj):
	if dobj==lightcrystal:
		game.addText("You shine the light crystal into the chasm. A few more meters of rocky chasm wall is visible in the light, but nothing else. ")
	else:
		game.addText("You're not about to start dropping your possessions into the chasm. ")
	return False
chasm4_2.setInVerbIobj = chasmSetIn
def chasmLookIn(game):
	game.addText("The chasm is wide, and empty. After a few metres, all you can see is black darkness. ")
	return False
chasm4_2.lookInVerbDobj = chasmLookIn
def chasmJumpIn(game):
	game.addText("You throw yourself into the chasm. ")
	global special_box_style
	
	chasm_ending.endGame(game)
	return False
chasm4_2.jumpInVerbDobj = chasmJumpIn
cave4_2.south_msg = "You carefully cross your improvised bridge. "
cave4_2.south_false_msg = "To the south is the chasm. There is currently no obvious way across. "
#LL ANTEROOM
cave_LL_ante = Room("Ladder Chamber, Upper Level", "You are in a tiny cavern. ")
cave_LL_ante.dark = True
ladder_LL = LadderConnector(cave4_2, cave_LL_ante)
ladder_LL.entranceA.describeThing("A ladder here leads up. ")
ladder_LL.entranceB.describeThing("A ladder here leads down. ")
l2door = DoorConnector(cave1, "n", cave_LL_ante, "s")
l2lock = Lock(True, l2key)
l2door.setLock(l2lock)

# CAVE 4 LL MAIN
# CAVE VISION 3
cave4 = Room("Caverns, Lower Level", "The cavern is a bit wider here. To the north is a deep chasm. ")
def cave4Arrive(game):
	global storm_caves
	if storm_turns_left==storm_turns_full or storm_caves > 1:
		return None
	storm_caves += 1
	game.addText("Three cloaked men appear before you, standing by the south door. \"We should put that damned opal back in the ground,\" says the man on the right, middle aged, and stout. \"We've done enough. Brother Neman is <i>dead</i>, for God's sake.\" The scrawny boy beside him lets out a shuddering sob, and the man places a hand on his shoulder. \"It's time to stop this madness.\"<br><br>The third man, tall and thin, with sneering eyes, clears his throat loudly. \"Brothers, please,\" he says. \"Our Order is devoted to science - to theosophy - to discovering the beyond. We must let go of our small fears, and fulfil the our Oath. Brother Neman gladly died for progress. If you are not willing to do the same, then perhaps you should die for your cowardice. I will hear no more of this.\"")
	return None
def cave4Discover(game):
	
	chasmAchievement.award(game)
	
cave4.arriveFunc = cave4Arrive
cave4.discoverFunc = cave4Discover
cave4.dark = True
cave4.e_false_msg = "Fallen rocks block the way east. "
chasm4 = chasm4_2.copyThingUniqueIx()
cave4.addThing(chasm4)
cave4.north = cave4_2
cave4.north_msg = "You carefully cross your improvised bridge. "
cave4.addThing(goldingot)
rocks4 = Thing("rocks")
rocks4.addSynonym("rock")
rocks4.setAdjectives(["large", "fallen", "east"])
rocks4.addSynonym("boulders")
rocks4._verbose_name = "fallen rocks"
rocks4.describeThing("Fallen rocks block the way to the east. ")
rocks4.xdescribeThing("Fallen rocks block the way to the east. ")
rocks4.invItem = False
rock_barriers.append(rocks4)
def rocks4Break(game):
	game.addText("The way east is now clear. ")
	cave4.east = cave5
rocks4.crushFunc = rocks4Break
def rocks4BreakDobj(game):
	game.addText("What would you like to break them with? ")
	game.parser.command.dobj = GrammarObj(target=rocks4)
	game.parser.command.verb = breakWithVerb
	game.parser.command.ambiguous = True
	return False
rocks4.breakVerbDobj = rocks4BreakDobj
cave4.addThing(rocks4)

# CAVE 5 LL E (Puzzle Box Combination, Chalice - blocked by rocks)
cave5 = Room("Caverns, Lower Level East", "This cavern is small, and unfinished, with curved walls of rough stone. ")
cave5.dark = True
for wall in cave5.walls:
	wall.xdescribeThing("The wall is made rough grey stone. ")
cave5.west = cave4
puzzleboxkey = Readable("tablet", "The sequence \"742364\" has been pressed into the clay tablet. ")
puzzleboxkey.setAdjectives(["small", "clay"])
puzzleboxkey.xdescribeThing("The tablet is a small rectangle of clay, with the numbers \"742364\" written on it. ")
puzzleboxkey.describeThing("There is a clay tablet here. There are numbers written on it. ")
puzzleboxkey.size = 15
cave5.addThing(puzzleboxkey)

# CAVE 6 LL W (Puzzle Box - requires key from the beach + porcelain star to break curse)
# CAVE VISION 6
cave6 = Room("Caverns, Lower Level West", "You are in a cavern a bit bigger than a small closet. ")
cave6.dark = True
### PUZZLEBOX ###
puzzlebox = Container("cube")
puzzlebox.setAdjectives(["small", "cube", "shaped"])
puzzlebox._verbose_name = "cube"
puzzlebox.cur_code = [0, 0, 0, 0, 0, 0]
def pbCodeStr():
	out = ""
	for d in puzzlebox.cur_code:
		out = out + str(d)
	return out
puzzlebox.codeStr = pbCodeStr
puzzlebox.describeThing("On the ground is a cube, with six numbers and six buttons on the top face. ")
puzzlebox.xdescribeThing(f"The cube has a mechanical display with six digits, currently {puzzlebox.codeStr()} . Under each of the six digits is a button, labeled 1 through 6. ")
cave6.addThing(puzzlebox)
def pbUnlockCheck(game):
	if puzzlebox.cur_code == [7, 4, 2, 3, 6, 4] and pb_lock.is_locked:
		pb_lock.makeUnlocked()
		puzzlebox.makeOpen()
		game.addText("The cube clicks open, revealing a key. ")
		global special_box_style
		
		puzzleBoxAchievement.award(game)
pb_button1 = Pressable("1")
pb_button1.addSynonym("button")
pb_button1.setAdjectives(["button"])
pb_button1.has_proper_name = True
pb_button1.describeThing("")
pb_button1.xdescribeThing("The button below the first digit is labeled \"1\".")
def b1func(game):
	puzzlebox.cur_code[0] = puzzlebox.cur_code[0] + 1
	puzzlebox.cur_code[3] = puzzlebox.cur_code[3] - 1
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button1.pressThing = b1func
puzzlebox.addComposite(pb_button1)
pb_button2 = Pressable("2")
pb_button2.addSynonym("button")
pb_button2.setAdjectives(["button"])
pb_button2.has_proper_name = True
pb_button2.describeThing("")
pb_button2.xdescribeThing("The button below the second digit is labeled \"2\".")
def b2func(game):
	puzzlebox.cur_code[0] = puzzlebox.cur_code[0] - 2
	puzzlebox.cur_code[1] = puzzlebox.cur_code[1] + 2
	puzzlebox.cur_code[3] = puzzlebox.cur_code[3] + 2
	puzzlebox.cur_code[4] = puzzlebox.cur_code[4] - 2
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button2.pressThing = b2func
puzzlebox.addComposite(pb_button2)
pb_button3 = Pressable("3")
pb_button3.addSynonym("button")
pb_button3.setAdjectives(["button"])
pb_button3.has_proper_name = True
pb_button3.describeThing("")
pb_button3.xdescribeThing("The button below the third digit is labeled \"3\".")
def b3func(game):
	puzzlebox.cur_code[5] = puzzlebox.cur_code[5] + 1
	puzzlebox.cur_code[2] = puzzlebox.cur_code[2] + 3
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button3.pressThing = b3func
puzzlebox.addComposite(pb_button3)
pb_button4 = Pressable("4")
pb_button4.addSynonym("button")
pb_button4.setAdjectives(["button"])
pb_button4.has_proper_name = True
pb_button4.describeThing("")
pb_button4.xdescribeThing("The button below the fourth digit is labeled \"4\".")
def b4func(game):
	puzzlebox.cur_code[0] = puzzlebox.cur_code[0] - 1
	puzzlebox.cur_code[3] = puzzlebox.cur_code[3] + 1
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button4.pressThing = b4func
puzzlebox.addComposite(pb_button4)
pb_button5 = Pressable("5")
pb_button5.addSynonym("button")
pb_button5.setAdjectives(["button"])
pb_button5.has_proper_name = True
pb_button5.describeThing("")
pb_button5.xdescribeThing("The button below the fifth digit is labeled \"5\".")
def b5func(game):
	puzzlebox.cur_code[0] = puzzlebox.cur_code[0] + 2
	puzzlebox.cur_code[1] = puzzlebox.cur_code[1] - 2
	puzzlebox.cur_code[3] = puzzlebox.cur_code[3] - 2
	puzzlebox.cur_code[4] = puzzlebox.cur_code[4] + 2
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button5.pressThing = b5func
puzzlebox.addComposite(pb_button5)
pb_button6 = Pressable("6")
pb_button6.addSynonym("button")
pb_button6.setAdjectives(["button"])
pb_button6.has_proper_name = True
pb_button6.describeThing("")
pb_button6.xdescribeThing("The button below the sixth digit is labeled \"6\".")
def b6func(game):
	puzzlebox.cur_code[5] = puzzlebox.cur_code[5] - 1
	puzzlebox.cur_code[2] = puzzlebox.cur_code[2] - 3
	i = 0
	for i in range(0, 6):
		if puzzlebox.cur_code[i] > 9:
			puzzlebox.cur_code[i] = puzzlebox.cur_code[i] - 10
		elif puzzlebox.cur_code[i] < 0:
			puzzlebox.cur_code[i] = 10 + puzzlebox.cur_code[i]
	game.addText("The digits on the cube now read " + puzzlebox.codeStr() + ". ")
	pbUnlockCheck(game)
pb_button6.pressThing = b6func
puzzlebox.addComposite(pb_button6)
puzzlebox.giveLid()
pb_lock = Lock(True, None)
puzzlebox.setLock(pb_lock)
pb_lock.setAdjectives(["cube", "cubes"])
pb_lock._verbose_name = "cube's lock"
pb_lock.xdescribeThing("The lock is hidden inside the shell of the cube. ")
depthskey = Key()
depthskey.setAdjectives(["thick", "sturdy", "puzzle", "cube"])
depthskey._verbose_name = "puzzle cube key"
depthskey.xdescribeThing("The key from the puzzle cube is thick and sturdy. ")
puzzlebox.addThing(depthskey)
caveLLWdoor = DoorConnector(cave4, "w", cave6, "e") # add a lock and key
llwlock = Lock(True, llwkey)
caveLLWdoor.setLock(llwlock)
cursedstar = Thing("star")
cursedstar.setAdjectives(["porcelain"])
cursedstar.describeThing("A porcelain star is mounted near the middle of the door. ")
cursedstar.xdescribeThing("It's a four point star made of translucent white porcelain. ")
cursedstar.broken = False
def breakStar(game):
	if cursedstar.broken:
		game.addText("The porcelain star is already broken. ")
	else:
		game.addText("You smash the porcelain star. ")
		cursedstar.broken = True
		cursedstar.describeThing("A few shards of porcelain remain attached to the door. ")
		cursedstar.xdescribeThing("The star is completely shattered. ")
		cursedstar.setAdjectives(["broken", "shattered", "porcelain"])
		cursedstar.addSynonym("porcelain")
		cursedstar._verbose_name = "shattered porcelain"
		global special_box_style
		
		curseAchievement.award(game)
	return False
cursedstar.breakVerbDobj = breakStar
cursedstar.kickVerbDobj = breakStar
#caveLLWdoor.entranceA.addComposite(cursedstar) # remove this and put is in the lens func
curse_scene = 0
def cLLWbarrier(game):
	global curse_scene
	if cursedstar.broken:
		return False
	else:
		game.addText("As you step through the door, your mind is filled with an image so vidid that you can hardly see what's in front of you. You see the opal touching the earth. Then, you see the island engulfed in a storm. The streets are flooded. Villagers scream and cry, or stand, staring expressionless at the sky. After a few moments, they start dropping dead. You are shown image after image of death, and destruction. ")
		scenarios = [f"{daughter.capNameArticle(True)} kneels by her fallen father, face wild with terror. Hands clasped at her chest, she screams a wordless prayer to her unhearing goddess, as tears stream down her face. ", "The vendor you spoke with at the market, who was so eager to help you, lies on the ground beside her stall. She trembles and gasps helpless as the storm water flows around her. Blood runs from a wound on her head. She sputters and coughs as the water level rises, her body jerking violently, until suddenly, she is still. She will never move again. ", "Ket the Picker stands on the shore, transfixed by the sky. A young boy, perhaps her brother, shakes her shoulder, crying, pleading. Ket hears nothing. The boy tugs her arm, and she falls sideways, hitting the ground like a sack of clothes. Still, she stares into the distance. She is not inside her body anymore. She is an empty husk. Her brother cries alone. ", "You recognize two boys you saw playing around town. One is dead now. The other struggles to carry him to higher ground. He whispers to the dead boy. \"It'll be all right,\" he says. \"We'll find the doctor. Don't be scared. I'm here. I won't leave you.\" He slips in the mud, and his head hits a rock. He doesn't get up. "]
		if curse_scene == len(scenarios):
			curse_scene = 0
		game.addText("Among them, you see familiar faces. " + scenarios[curse_scene])
		game.addText("Eventually, the vision vanishes, and you find yourself back where you began. ")
		if curse_scene < len(scenarios):
			curse_scene = curse_scene + 1
		return True
caveLLWdoor.barrierFunc = cLLWbarrier
def cave4Reveal(game):
	if cursedstar.parent_obj:
		game.addText("Looking through the lens reveals nothing further. ")
		return True
	else:
		game.addText("Looking through the lens, you can see a porcelain star mounted on the west door. ")
		caveLLWdoor.entranceA.addComposite(cursedstar)
		return True
cave4.lensReveal = cave4Reveal
# CAVE 7 (The Depths - bury the opal - contains Ceremonial Blade)
# CAVE VISION 7
cave7 = Room("Caverns, Depths", "You are in a wide cavern, deep in the earth. ")
def cave7Arrive(game):
	global storm_caves
	if storm_turns_left==storm_turns_full or storm_caves > 2:
		return None
	storm_caves += 1
	
	game.addText(f"\"Revered Brother!\" cries a young man's voice. \"The opal vein below us! It's resonating with the same frquency the sample is picking up! I think they're still connected. The reaction is getting too much energy. God only knows what'll happen if this blows - what forces could enter our world. We have to - \"<br><br>With a blast, a bright arc connects the ground below with something far above. It snakes through the passageways, shining silver white, and crackling, before vanishing in an instant.<br><br>What you have just experienced is a memory, but it isn't yours. It's a memory of this place. ")
	return None
cave7.arriveFunc = cave7Arrive
cave7.dark = True
fan = Thing("fan")
fan.setAdjectives(["painted", "hand", "held", "handheld"])
fan._verbose_name = "painted fan"
fan.describeThing("On the ground is a hand held fan, painted with a feather pattern, reminiscent of a seagull's wing. ")
fan.xdescribeThing("The fan's surface is covered in painted feathers, mostly white, with a line of black along the leading edge. ")
def fanUse(game):
	game.addText("You fan yourself a bit. ")
	return False
fan.useVerbDobj = fanUse
cave7.addThing(fan)
prayer1 = Readable("prayer", "You read the words carved into the cavern wall. <br><br><i>You who brings the rain, I pray thee, listen. <br>You who protects this land, <br>You who kills the interloper; sinks ships; holds our hearts - <br>Hear my cry, O Goddess of the Storm, <br>Come before me now, <br>See my flesh and soul, <br>Take the gifts I offer. Hear my request. <br>So be it.</i> ")
def prayer1func(game):
	game.addText(prayer1.read_desc)
	goddess_abs.addSpecialTopic(prayer_topic1)
prayer1.readText = prayer1func
prayer1.addSynonym("carving")
prayer1.addSynonym("poem")
prayer1.setAdjectives(["carved"])
cave7.north_wall.addComposite(prayer1)
prayer1.describeThing("A poem or prayer has been carved into the north wall. ")
prayer1.xdescribeThing("A poem or prayer has been carved into the north wall. ")

# DEPTHS ANTE
depths_ante = Room("Ladder Chamber, Lower Level", "You are in a small cavern. ")
ladder_depths = LadderConnector(cave7, depths_ante)
depths_ante.dark = True
depths_entrance = DoorConnector(cave4, "s", depths_ante, "n")
depths_lock = Lock(True, depthskey)
depths_entrance.setLock(depths_lock)

cavegroup.setMembers([cave0, cave1, cave2, cave3, cave4, cave4_2, cave5, cave6, cave7, cave_LL_ante, depths_ante])

for key, room in rooms.items():
	g = goddess_abs.copyThing()
	if isinstance(room, Room):
		room.addThing(g) 

# FUNCTIONS
def opening(game):
	game.addText("<b>ISLAND OF THE BLESSED: by JSMaika</b><br>  You are a sailor, on a long, solo journey across the Yalukan Ocean. You have passed many days alone on your little boat, and you will pass many more before you reach your homeland. One evening, as you are navigating through a small, mapped area in otherwise uncharted waters, you find yourself suddenly in the middle of a violent storm. You are blown off course - far off course. It is all you can do to keep from capsizing.  Despite your desperate attempts, you fail to escape the storm. The waves are dark mountains around you; titans, ready to swallow you whole, or crush you beneath their weight. You hold your tiny boat steady, riding wave after giant wave. You are cold, soaked to the skin. Your fingers ache as you tug the ropes. You are fading.  You are thrown suddenly out of your boat. Your body crashes against something hard, knocking the wind out of you. You have a sense, for a moment, of an inhuman presence, of something reaching toward you, before the world fades to nothing.  Welcome to <i>Island in the Storm</i>. Type INSTRUCTIONS for instructions.")

game.gameOpening = opening

screen = app.primaryScreen()
screen = screen.size()
box_style1 = "QFrame {background-color: #232323; border: 1px solid #ffffff; border-radius:0px; margin-bottom: 15px} QLabel {color: #ffffff; border: none; font-size: 18px;}"
box_style2 = "QFrame {background-color: #3a3a01; border: 2px solid #edf424; border-radius:0px; margin-bottom: 15px} QLabel {color: #edf424; border: none; font-size: 18px;}"
special_box_style = "QFrame {background-color: #210111; border: 2px solid #f4245c; border-radius:0px; margin-bottom: 15px} QLabel {color: #f4245c; border: none; font-size: 18px;}"
app_style = """
	#MainWindow {
		background-image: url(island_bg2.png);
		background-color: #000000;
	}
	QLineEdit {
		background: #ffffff;
		font-size: 18px;
	}
"""
scroll_style = """
	/* VERTICAL */
	QWidget {
		background-color: transparent;
		background-image: none;
		border: none;
	}
	QScrollBar:vertical {
		border: none;
		background: #a3a3a3;
		border-radius: 6px;
		width: 30px;
		margin: 10px 8px 10px 8px;
	}

	QScrollBar::handle:vertical {
		background: #ffffff;
		border-radius: 6px;
		min-height: 15px;
	}

	QScrollBar::add-line:vertical {
		background: none;
		height: 10px;
		subcontrol-position: bottom;
		subcontrol-origin: margin;
	}

	QScrollBar::sub-line:vertical {
		background: none;
		height: 10px;
		subcontrol-position: top left;
		subcontrol-origin: margin;
		position: absolute;
	}

	QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
		background: none;
	}

	QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
		background: none;
	}

    """

game.initGame()
ex.show()
sys.exit(app.exec_())

