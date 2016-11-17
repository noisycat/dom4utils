#modname "rpgemgen.dm"
#description "Allows for the use of a Automaton and Gem Factories to speed up debug games. Could possibly be entertaining for Friday Night Madness"
#version 0.90
#domversion 4.21
#newmonster 
#name "Automaton"
#descr "This guy generates gems and research points. Each one does 50rp."
#gcost 0
#size 2
#prot 0
#mr 10
#mor 10
#str 10
#att 10
#def 10
#prec 10
#enc 0
#mapmove 3
#ap 12
#eyes 2
#magicbeing
#amphibian
#startage 25
#maxage 1000
#heal
#fixedresearch 50
#end
#newmonster 
#name "Doozer's Dummy"
#descr "This guy generates gems and research points. Each one does 50rp."
#gcost 0
#size 2
#prot 0
#mr 10
#hp 2000
#mor 30
#str 10
#att 10
#prot 20
#def 0
#prec 10
#enc 0
#mapmove 3
#ap 12
#eyes 2
#amphibian
#startage 1
#maxage 1000
#end
#newsite
#name "Gem Factory"
#descr "Legends holds of gem factories that produce magical gems from ground up faeries... and gold from their wings"
#rarity 5
#mon "Doozer's Dummy"
#com "Doozer's Dummy"
#com "Automaton"
#gems 0 99
#gems 1 99
#gems 2 99
#gems 3 99
#gems 4 99
#gems 5 99
#gems 6 99
#gems 7 99
#gold 500
#supply 500
#res 500
#end
