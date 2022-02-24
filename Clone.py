import os
import sys
import shutil

"""
This function removes any uneccecary elements
    when splitting paths into an array.
"""
def shave(lst):
    while '' in lst or ' ' in lst:
        if '' in lst:
            lst.remove('')
        if ' ' in lst: 
            lst.remove(' ')


"""
This quite vulgar variable nobullshit
    and not so vulgar chSum are just shortcuts 
    to give the input and output and the check sum without all
    the text
"""


nobullshit = False
chSum = False
altMount = False

#This is here because debian based OS's (or at least Ubuntu's)
# lsblk does not have the column 'mountpoints', it has 'mountpoint' without the 's'; just so that there's not a lot of errors, just check in the beginning
print('Checking lsblk columns...')
res = os.popen('lsblk -o mountpoints -n').read()
if res == '':
    print('Swapping command parameters...')
    altMount = True
    
inFile = ''
outFile = ''

if '-nbs' in str(sys.argv):
    nobullshit = True
    if '-cs' in str(sys.argv):
        chSum = True

if not(nobullshit):
    print('\n--||REMINDER: Run this as a superuser to clone devices||--\n')

    while True:
        res = input('Would you like the program to run a checksum (md5) immedietly after the cloning process? (y/n)\n>> ')
        res = res.lower()
        if res == 'y' or res == 'n':
            if res == 'y':
                chSum = True
            break

    #demoun == device mounts, originally just for mounts,
    #          but now holds the type and size as well
    demoun = dict()
    devices = {}
    hold = {}

    #Retrieve all devices
    res = os.popen('lsblk -o name -n -l').read()
    devices = res.split('\n')
    shave(devices)

    #CLI stuff
    string = 'Devices: {} | Type: {} | Size: {} | Connected Mountpoints: '.format(''.ljust(6,' '),''.ljust(10,' '),''.ljust(5,' '))
    division = ''.ljust(16,'-') + '+' + ''.ljust(18,'-') + '+' + ''.ljust(13,'-') + '+' + ''.ljust(40,'-')
    print(division)
    print(string)
    print(division)
    for i in range(len(devices)):
        #Mounts holds the amount of connected mountpoints connected to a device
        mounts = 0
        
        #check for different columns
        if altMount:
            res = os.popen(('lsblk -o mountpoint -n -l /dev/{}'.format(devices[i]))).read()
        else:
            res = os.popen(('lsblk -o mountpoints -n -l /dev/{}'.format(devices[i]))).read()
        
        res = res.split('\n')
        shave(res)
        #Store mounts for array iteration purposes later on
        mounts = len(res)


        hold = os.popen(('lsblk -o size -n -s -l /dev/{}'.format(devices[i]))).read()
        hold = hold.split('\n')
        shave(hold)
    
        while len(hold) > 1:
            hold.pop(len(hold)-1)
        hold[0].strip()
        res.append(hold[0])
        hold = os.popen(('lsblk -o type -n -s -l /dev/{}'.format(devices[i]))).read()
        hold = hold.split('\n')
        shave(hold)
    
        while len(hold) > 1:
            hold.pop(len(hold)-1)
    
        hold[0].strip()

        #The rest of this is just for CLI formatting
        if hold[0] == 'part':
            hold[0] = 'Partition'
        elif hold[0] == 'disk':
            hold[0] = 'Disk Block'
        elif hold[0] == 'loop':
            hold[0] = 'Loop Device'
        elif hold[0] == 'rom':
            hold[0] = 'R.O.M.'
    
        res.append(hold[0])
        iterator = 0
        string = ''.ljust(8,' ') + devices[i].ljust(7, ' ') + ' | ' + ''.ljust(5, ' ') +  res[mounts+1].ljust(11,' ') + ' | ' + ''.ljust(5, ' ') +  res[mounts].ljust(6,' ') + ' | '
        
        #Check if there are no mounts, avoid CLI clutter of new lines and uneccessary formatting
        if mounts != 0:
            string += res[iterator]
    
        iterator += 1
    
        if mounts > 1:
            for j in range(mounts):
                if (j) == mounts-1:
                    break
                string += '\n'
                string += ''.ljust(16, ' ')+'|'+''.ljust(18,' ')+'|'+''.ljust(13,' ')+'| '
                string += res[iterator+j]
    
        print(string)
        print(division)
        #Add the array to the dictonary for root directory checks and further CLI output
        demoun[devices[i]] = res
    
    print('\n--||REMINDER: Run this as a superuser to clone devices||--\n')
    
    while True:
        inFile = input('Type device to clone:\n    e.g. ">> sdb2" or ">> /dev/loop0"\n>> ')
        inFile = inFile.strip()
        inFile = inFile.split('/')
        #Just remove /dev/, it's hardcoded to /dev/ as the valid devices
        #   selection is in /dev/ anyways. Just a placebo so I don't have to
        #   determine which format is which
        if 'dev' in inFile:
            inFile.remove('dev')
    
        if len(inFile) > 1:
            inFile.remove('')
        
        if len(inFile) > 1:
            inFile.remove('')
        
        inFile = inFile[0]
        
        if inFile in demoun.keys():
            if '/' in demoun[inFile]:
                    print("\n--||You cannot clone the device containing the filesystem\n")
            else:
                break
        else:
            print('\n--||You did not choose one of the devices.\n')

    h = inFile

    inFile = '/dev/{}'.format(inFile)

    outFile = input('\nType the specic path and file to clone {} [{} {}] to\n>> '.format(inFile,demoun[h][len(demoun[h])-2].strip(),demoun[h][len(demoun[h])-1]))
    print('\n:: Starting the cloning process...')
    print('(Multi-Gigabyte devices, especially Disk Blocks,  may take a long time to clone)')

#If all of the 'bullshit' was skipped
if nobullshit:
    inFile = input('In:  ')
    outFile = input('Out: ')
    print('\n:: Starting the cloning process...')

shutil.copy(inFile,outFile)
print('\nCompleted.\n')

#Checksum
if chSum:
    print(':: Running md5 checksum of {}...'.format(inFile))
    donorSum = os.popen('md5sum {}'.format(inFile)).read()
    donorSum = (donorSum.split(' '))[0]
    print('{}\'s md5 checksum:\n{}\n'.format(inFile,donorSum))
    print(':: Running md5 checksum of {}...'.format(outFile))
    cloneSum = os.popen('md5sum {}'.format(outFile)).read()
    cloneSum = (cloneSum.split(' '))[0]
    print('{}\'s md5 checksum:\n{}\n'.format(outFile,cloneSum))
    if donorSum == cloneSum:
        print('Checksums match. Successful clone.\n')
    else:
        print('Checksums do not match. Failure to clone.\n')
