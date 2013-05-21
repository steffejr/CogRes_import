'''
Created on Jul 19, 2012

@author: jason
'''

def subffnListImages(study,ImageType='T1',prefix='',prefixExc=''):
    ''' function to find files with specific types, with or without prefixes. 
    And can be used to look for prefixes of one type but not another.''' 
    print 'Looking for: ' + ImageType
    if len(prefixExc):
        print 'but not with: ' + prefixExc
    for subject in study.subjectlist:
        for visit in subject.visitlist:
            if len(prefixExc):
                if (prefix+ImageType in visit.niftis[ImageType]) and not (prefixExc+ImageType in visit.niftis[ImageType]):
                    print visit.niftis[ImageType][prefix+ImageType].path
            elif (prefix+ImageType in visit.niftis[ImageType]):
                print visit.niftis[ImageType][prefix+ImageType].path                    

def subfnListSubjectsInQuar(study):
    for subject in study.quarantine.subjectlist:
        for visit in subject.visitlist:
            print visit.niftis['T1']