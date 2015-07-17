import minqlbot
import random
import time

# Allow everybody to cap / Vote for captain
# Allow everybody to fill / Only allow Captains
# Allow automatic cointoss
# Enforce teams

class sub:
    def __init__(self, name, team):
        self.subName = name
        self.subTeam = team

class pugInfo():
    def __init__(self, pug):
        self.pug = pug
        self.currentlist = []
        self.vipPlayer = []
        self.teamSize = 8
        self.autoCointoss = True
        self.forcePick = True
        self.forceTurn = True
        self.enforcePUG = False
        self.manageSub = True
        self.game = pugGame(self, pug)

    def printList(self):
        list = []
        if len(self.currentlist) > 0:
            for p in self.currentlist:
                list.append("^3{},".format(p.name))
        else:
            list.append("^7<Empty>")
        self.pug.msg("^7List: {} ^7".format("".join(list)))

    def setTeamsize(self, channel, size):
        self.teamSize = size
        channel.reply("^7 PUG size has been set to {}".format(self.teamSize))
        
class pugGame():
    def __init__(self, info, pug, captains = None):
        self.info = info
        self.pug = pug
        self.currentpool = []
        self.teamBlue = []
        self.teamRed = []
        self.subs = []
        self.captains = []
        self.isPicking = False
        self.pickTurn = ""
        self.firstPick = ""
        if captains is not None:
            self.captains = captains

    def start(self):
        self.isPicking = True
        self.captains[0].put("red")
        self.captains[1].put("blue")
        self.teamRed.append(self.captains[0])
        self.teamBlue.append(self.captains[1])
        for i in range(0, self.info.teamSize):
            if self.info.currentlist[i] not in self.captains:
                self.currentpool.append(self.info.currentlist[i])

    def add(self, player):
        if player not in self.info.currentlist:
            if player in self.info.vipPlayer and self.isPicking == False:
                self.info.currentlist.insert(0, player)
            else:
                self.info.currentlist.append(player)
            self.pug.msg("^7{} ^2has been added ^7- Total : {} Players".format(player.name, len(self.info.currentlist)))

    def remove(self, player):
        if self.isPicking:
            if player in self.captains:
                self.info.game = pugGame(self.info, self.pug)
                self.pug.unlock()
                self.pug.msg("^7PUG Cancelled : Cap by typping !cap to restart picks")
                return
            else:
                if player in self.teamRed:
                    self.teamRed.remove(player)
                if player in self.teamBlue:
                    self.teamBlue.remove(player)
                if player in self.currentpool:
                    self.currentpool.remove(player)
                    if len(self.currentlist) > 8:
                        self.currentpool.add(self.currentlist[8])
                if player.team != "spectator":
                    player.put("specator")
        self.pug.msg("^7{} ^2has been removed".format(player.name))

    def cap(self, player):
        if player in self.captains:
            self.captains.remove(player)
            player.put("spectator")
            self.pug.msg("{} ^7 is no longer team captain".format(player.name))
        elif len(self.info.currentlist) >= self.info.teamSize:   
            for i in range(0, self.info.teamSize):
                if player == self.info.currentlist[i]:
                    if len(self.captains) > 1:
                        self.pug.msg("^7Action Denied : There is already 2 captains")
                        return
                    self.captains.append(player)
                    self.pug.msg("{} ^7 is now team captain".format(player.name))
                    
                    if len(self.captains) > 1:
                        self.pug.restart(False)
                        self.pug.delay(15, self.pug.startpicking())
        else:
            self.pug.msg("^7Action Denied : There is not enough players")

    def printList(self):
        list = []
        if len(self.currentpool) > 0:
            for p in self.currentpool:
                list.append("^3{},".format(p.name))
        else:
            list.append("^7<Empty>")
        self.pug.msg("^7List: {} ^7".format("".join(list)))

class pug(minqlbot.Plugin):
    def __init__(self):
        super().__init__()
        self.pugInfo =  pugInfo(self)
        self.commandList = "^7 PUG Commands : ^6!add^7 , ^6!remove^7 , ^6!sub^7 , ^6!cap^7 , ^6!list^7 , ^6!queue^7 , ^7PUG-Commands : ^6!pug^7 <^5size^7|^5autocointoss^7|^5forcePick^7|^5forceTurn^7|^5managesub^7|^5enforce^7>"

        self.add_hook("game_end", self.event_game_end)
        self.add_hook("game_start", self.event_game_start)
        self.add_hook("player_connect", self.event_player_connect)
        self.add_hook("player_disconnect", self.event_player_disconnect)

        self.add_command("pug", self.cmd_pug, 4, usage="(help | autocointoss | enforce | forcePick | size)")
        self.add_command("add", self.cmd_add)
        self.add_command("remove", self.cmd_remove)
        self.add_command("list", self.cmd_list)
        self.add_command("pick", self.cmd_pick)
        self.add_command(("repick", "restart", "restart"), self.cmd_reset)
        self.add_command(("cap", "captain"), self.cmd_cap)
        self.add_command(("queue", "fulllist"), self.cmd_queue)
        self.add_command("sub", self.cmd_sub)
        
    def tell_motd(self, player):
        self.tell(self.commandList, player)

    def getPlayer(self, player):
        if isinstance(player, str):
            for p in self.players():
                if p in player.name:
                    return p
        else:
            for p in self.players():
                if p is player:
                    return p


    def restart(self, unlock):
        self.pugInfo.game = pugGame(self.pugInfo, self, self.pugInfo.game.captains)
        self.lock()
        for p in self.players():
            if p.team != "spectator":
                p.put("spectator")
        if unlock:
            self.unlock()
            
    def startpicking(self):
        self.pugInfo.game = pugGame(self.pugInfo, self, self.pugInfo.game.captains)
        self.pugInfo.game.start()
        if self.pugInfo.autoCointoss:
            i = random.randint(0, 100)
            if i >= 50:
                self.pugInfo.game.pickTurn = self.pugInfo.game.captains[0].team
                self.pugInfo.game.firstPick = self.pugInfo.game.captains[0].team
                self.msg(" ^3{} ^7won the cointoss!".format(self.pugInfo.game.captains[0]))
            else:
                self.pugInfo.game.pickTurn = self.pugInfo.game.captains[1].team
                self.pugInfo.game.firstPick = self.pugInfo.game.captains[1].team
                self.msg(" ^3{} ^7won the cointoss!".format(self.pugInfo.game.captains[1]))
                
    def printList(self):
        if self.pugInfo.game.isPicking:
            self.pugInfo.game.printList()
        else:
            self.pugInfo.printList()


    def event_game_end(self, game, score, winner):
        for p in self.players():
            if p.team is winner:
                self.pugInfo.vipPlayer.append(p)
        self.pugInfo.game.captains = []
        
    def event_game_start(self, game):
        if self.pugInfo.enforcePUG:
            if not self.pugInfo.game.isPicking:
                Game.abort()
                self.msg("^7 Game cannot start without a list - Type ^6!pug help ^7for the command list")
        self.pugInfo.game.isPicking = False
        for i in range(0, self.pugInfo.teamSize):
            self.pugInfo.currentlist.pop(0)
        self.unlock()

    def event_player_connect(self, player):
        self.delay(15, self.tell_motd, args=(player))
        
    def event_player_disconnect(self, player, reason):
        if player in self.pugInfo.currentlist:
            self.pugInfo.currentlist.remove(player)
        
        if player in self.pugInfo.game.captains:
            self.pugInfo.game.captains.remove(player)

    def event_team_switch(self, player, old_team, new_team):
        if self.pugInfo.game.isPicking:
            if player not in self.pugInfo.game.currentpool:
                player.put("spectator")
            elif self.pugInfo.forcePick and player.team is not new_team:
                player.put("spectator")
            
    def cmd_add(self, player, msg, channel):
        if len(msg)  > 1:
            if self.has_permission(player, 2):
                for p in self.players():
                    if msg[1].lower() in p.clean_name.lower():
                        self.pugInfo.game.add(p)
        else:
            self.pugInfo.game.add(player)

    def cmd_remove(self, player, msg, channel):
        if len(msg) == 1:
            self.pugInfo.game.remove(player)
        else:
            if self.has_permission(player, 2):
                for p in self.pugInfo.currentlist:
                    if msg[1].lower() in p.clean_name.lower():
                        self.pugInfo.game.remove(p)

    def cmd_sub(self, player, msg, channel):
        if len(msg)  > 1:
            if self.has_permission(player, 5):
                p = self.getPlayer(msg[1])
                if p.team is not "spectator":
                    if self.game().state == "in_progress":
                        Game.pause()
                    self.pugInfo.game.subs.append(sub(p.name, p.team))
                    channel.reply("^7 Sub is required for ^8 {} ^7 type ^6!sub^7 to fill".format(p.name))
                else:
                    p.put(self.pugInfo.game.subs[0].subTeam)
                    Game.unpause()
        else:
            if player is not "spectator":
                if player in self.pugInfo.game.captains and self.pugInfo.game.isPicking:
                    self.restart(True)
                    self.pugInfo.game.captains = []
                else:
                    if self.game().state == "in_progress":
                        Game.pause()
                    self.pugInfo.game.subs.append(sub(p.name, p.team))
                    channel.reply("^7 Sub is required for ^8 {} ^7 type ^6!sub^7 to fill".format(p.name))
            else:
                if self.pugInfo.manageSub:
                    channel.reply("^7Action Denied : Only captains can select subs")
                else :
                    if len(self.pugInfo.game.subs) is not 0:
                        player.put(self.pugInfo.game.subs[0].subTeam)
                        Game.unpause()
            
    def cmd_cap(self, player, msg, channel):
        if self.game().state == "in_progress":
            channel.reply("^7Action Denied : Game is in progress")
            return
        if len(msg)  > 1:
            if self.has_permission(player, 5):
                for i in range(0, self.pugInfo.teamSize):
                    if msg[1] in self.pugInfo.currentlist[i].clean_name.lower():
                        self.pugInfo.game.cap(self.pugInfo.currentlist[i])
                        return
        else:
            self.pugInfo.game.cap(player)

    def cmd_pick(self, player, msg, channel):
        if len(msg)  > 1:
            if player in self.pugInfo.game.captains:
                if not self.pugInfo.forcePick or (self.pugInfo.game.pickTurn is player.team):
                    for p in self.pugInfo.game.currentpool:
                        if msg[1].lower() in p.clean_name.lower():
                            if player.team == "red":
                                self.pugInfo.game.teamRed.append(p)
                                self.pugInfo.game.pickTurn = "blue"
                            else:
                                self.pugInfo.game.teamBlue.append(p)
                                self.pugInfo.game.pickTurn = "red"
                            p.put(player.team)
                            self.pugInfo.game.currentpool.remove(p)
                            self.printList(channel)
                else:
                    channel.reply("^7Action Denied : Wait for your turn to pick")

    def cmd_list(self, player, msg, channel):
        self.printList()

    def cmd_queue(self, player, msg, channel):
        self.pugInfo.printList()

    def cmd_reset(self, player, msg, channel):
        if player in self.pugInfo.game.captains and self.pugInfo.game.isPicking or self.has_permission(player, 5):
            firstPick = self.pugInfo.game.firstPick
            self.restart(False)
            self.pugInfo.game.pickTurn = firstPick
            self.pugInfo.game.isPicking = true
            channel.reply("^7  Picks have been restarted.  Type ^6!pick <name>^7 to start picking")

    def  cmd_pug(self, player, msg, channel):
        if len(msg) >= 2:
            command = msg[1].lower()

            if len(msg) >= 3:
                if self.has_permission(player, 2):
                    if command == "size":
                        self.pugInfo.setTeamsize(channel, int(msg[2]))
            else:
                if command == "help":
                    channel.reply(self.commandList)

                if self.has_permission(player, 2):
                    if command == "forcepick":
                        self.pugInfo.forcePick = not self.pugInfo.forcePick
                        if self.pugInfo.forcePick :
                            channel.reply("^6 !Pick ^7is now required to pick players - Players cannot join unless they are picked")
                        else:
                            channel.reply("^6 !Pick ^7is no longer required")

                    if command == "forceturn":
                        self.pugInfo.forceTurn = not self.pugInfo.forceTurn
                        if self.pugInfo.forceTurn :
                            channel.reply("^7 Force turn is now Enabled - Captains have to wait after each other in order to pick")
                        else:
                            channel.reply("^7 Force turn is now Disabled")

                    elif command == "autocointoss":
                        self.pugInfo.autoCointoss = not self.pugInfo.autoCointoss
                        if self.pugInfo.autoCointoss :
                            channel.reply("^6 Auto Cointoss^7 has been enabled - One captain will randomly be chosen as winner of the cointoss")
                        else:
                            channel.reply("^6 Auto Cointoss^7 has been disabled")

                    elif command == "managesub":
                        self.pugInfo.manageSub = not self.pugInfo.manageSub
                        if self.pugInfo.manageSub :
                            channel.reply("^6 Sub Management^7 has been enabled - Only captains will be able to choose who can replace their player")
                        else:
                            channel.reply("^6 Sub Management^7 has been disabled")

                    elif command == "enforce":
                        self.pugInfo.enforcePUG = not self.pugInfo.enforcePUG
                        if self.pugInfo.enforcePUG :
                            channel.reply("^7 PUG is now enforced - Match cannot start without picking team")
                        else:
                            channel.reply("^7 PUG is no longer enforced")
