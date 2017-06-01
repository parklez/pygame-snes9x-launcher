#############################
directory = 'Roms/'

emulator_name = 'snes9x-x64'

launch_options = '-fullscreen'
#############################
import os

games = sorted(os.listdir(directory))

def launch(game):
    os.system(emulator_name + ' ' + launch_options + ' ' + '"' + game + '"')

def interface():
    i = 0
    print('SNES Command-Line Interface')
    print('-'*30)
    for game in games:
          print(i, game)
          i += 1
    print('-'*30)

def main():
    while True:
        interface()
        
        game = input('Game number: ')
        
        if game.isdigit() and int(game) <= len(games)-1:
            launch(games[int(game)])
                
        else:
            print('\nThere is no such game with that number! :C\nPress [ENTER] to continue.')
            input()

if __name__ == '__main__':
    main()
