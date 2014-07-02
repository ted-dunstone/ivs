# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 22:44:23 2014

@author: Joshua Abraham
@description: eft/an2 NIST image converter/re-packager using NIST NBIS binaries
        Note: To run this script use:

              python convert_NIST_finger.py -i <input_file>  -f <image_format> [-o <output_file>]

              e.g. python convert_NIST_finger.py -i file.eft  -f wsq file_new.eft
              
"""

import os
import sys
import getopt
import shutil
import json
import subprocess
import numpy as np


#NIST binary path
nist_path="NIST_linux_x86_64_binary/"

record_type_1_to_map={
                    "1.001":"LOGICAL RECORD LENGTH", 
                    "1.002":"VERSION NUMBER",
                    "1.003":"FILE CONTENT",
                    "1.004":"TYPE OF TRANSACTION",
                    "1.005":"DATE",
                    "1.006":"PRIORITY",
                    "1.007":"DESTINATION AGENCY IDENTIFIER",
                    "1.008":"ORIGINATING AGENCY IDENTIFIER",
                    "1.009":"TRANSACTION CONTROL NUMBER",
                    "1.010":"TRANSACTION CONTROL REFERENCE",
                    "1.011":"NATIVE SCANNING RESOLUTION",
                    "1.012":"NOMINAL TRANSMITTING RESOLUTION",
                    "1.013":"DOMAIN NAME",
                    "1.014":"GREENWICH MEAN TIME",
                    "1.015":"DIRECTORY OF CHARACTER SETS",
             }

record_type_2_to_map={
                      "2.001":"LOGICAL RECORD LENGTH", 
                      "2.002":"INFORMATION DESIGNATION CHARACTER"
}


record_type_4_to_map={
                    "4.001":"RECORD HEADER", 
                    "4.002":"INFORMATION DESIGNATION CHARACTER",
                    "4.003":"IMPRESSION TYPE",
                    "4.004":"FRICTION RIDGE GENERALIZED POSITION",
                    "4.005":"IMAGE SCANNING RESOLUTION",
                    "4.006":"HORIZONTAL LINE LENGTH",
                    "4.007":"VERTICAL LINE LENGTH",
                    "4.008":"COMPRESSION ALGORITHM",
                    "4.009":"IMAGE DATA",
}


record_type_14_to_map={
                    "14.001":"LOGICAL RECORD LENGTH", 
                    "14.002":"IMAGE DESIGNATION CHARACTER",
                    "14.003":"IMPRESSION TYPE",
                    "14.004":"SOURCE AGENCY/ORI",
                    "14.005":"TENPRINT CAPTURE DATE",
                    "14.006":"HORIZONTAL LINE LENGTH",
                    "14.007":"VERTICAL LINE LENGTH",
                    "14.008":"SCALE UNITS",
                    "14.009":"HORIZONTAL PIXEL SCALE",
                    "14.010":"VERTICAL PIXEL SCALE",
                    "14.011":"COMPRESSION ALGORITHM",
                    "14.012":"BITS PER PIXEL",
                    "14.013":"FINGER POSITION",
                    "14.020":"COMMENT",
                    "14.999":"IMAGE DATA",
}



finger_position_codes={"0":"UNKNOWN", 
                    "1":"Right thumb",
                    "2":"Right index finger",
                    "3":"Right middle finger",
                    "4":"Right ring finger",
                    "5":"Right little finger",
                    "6":"Left thumb",
                    "7":"Left index finger",
                    "8":"Left middle finger",
                    "9":"Left ring finger",
                    "10":"Left little finger",
                    "11":"Plain right thumb",
                    "12":"Plain left thumb",
                    "13":"Plain right four fingers",
                    "14":"Plain left four fingers"
}


#define X-Y coordinate NIST fields
x_dim_recs=["3.6.1.1", "4.6.1.1", "5.6.1.1", "6.6.1.1",
                 "7.6.1.1", "8.6.1.1", "9.6.1.1", "10.6.1.1", "11.6.1.1", "12.6.1.1",]
                 
y_dim_recs=["3.7.1.1", "4.7.1.1", "5.7.1.1", "6.7.1.1",
                 "7.7.1.1", "8.7.1.1", "9.7.1.1", "10.7.1.1", "11.7.1.1", "12.7.1.1",]

x_dim_fields=["4.006", "14.006",]
                 
y_dim_fields=["4.007", "14.007",]



def getMinutiae(path, finger_name):
        X, Y=0, 0
        md1, md2, mdo1, mdo2=[], [], [], []
        b1, b2, b3, b4=0, 0, 0, 0
        MIN_Q=0.2

        if(finger_name!=None): 
                fh = open(path+finger_name+".min", "r")
                line = fh.readline()
                fields = line.split(' ')
                X=float(fields[2])#/scale
                Y=float(fields[3])#/scale

                
                for i in range(3):
                        fh.readline()
                        
                orient_map_fh = open(path + finger_name+".dm", "r")
                quality_map_fh = open(path + finger_name+".qm", "r")
                hc_map_fh = open(path + finger_name+".hcm", "r")

                orient_img=[]
                quality_map=[]
                hc_map=[]

                #Get the orientation map
                i=0
                for line in orient_map_fh.readlines():
                        j=0
                        orient_img_t=[]
                        for s in line.split(' '):
                                try:
                                        orient_img_t.append(float(s)*11.25)
                                        j=j+1
                                except ValueError:
                                        continue
                        orient_img.append(orient_img_t)
                        i=i+1

                #Get the quality map
                i=0
                for line in quality_map_fh.readlines():
                        j=0
                        q_img_t=[]
                        for s in line.split(' '):
                                try:
                                        q_img_t.append(int(s))
                                        j=j+1
                                except ValueError:
                                        continue
                        quality_map.append(q_img_t)
                        i=i+1


                #Get the high curvature map
                i=0
                for line in hc_map_fh.readlines():
                        j=0
                        h_img_t=[]
                        for s in line.split(' '):
                                try:
                                        h_img_t.append(int(s))
                                        j=j+1
                                except ValueError:
                                        continue
                        hc_map.append(h_img_t)
                        i=i+1

                minutiae=[]

                lines=fh.readlines()

                ang_m_list={}
                
                #Get minutiae
                
                for line in lines:
                        line=line.replace(':',',')
                        line=line.replace(';',',')
                        fields = line.split(',')

                        m_type=fields[5].strip()
                            
                        if float(fields[4]) < MIN_Q:
                                continue
                        ang_m_list[int(fields[1])*1000 + int(fields[2])]=float(fields[3])*11.25 * float(np.pi) / 180.0
                        ## <index> <x><y><normalised x>, <normalised y>, direction,  quality, type                                      
                        minutiae.append({"index": int(fields[0]), "x": int(fields[1]), "y":Y-int(fields[2]), "theta":float(fields[3])*11.25*np.pi/180, "quality":float(fields[4]), "type":m_type })
                      
#                fingerprints.append([f[0:len(f)-4], minutiae,  neighbours, [core_x,  core_y], [ncore_x,  ncore_y],  orients, radii,[float(core_x)/dimX, float(core_y)/dimY,core_x, core_y]]     )

                orient_map_fh.close()
                quality_map_fh.close()
                hc_map_fh.close()
                fh.close()
                
        return minutiae #,  dimX,  dimY



#valid image formats for transformation
valid_image_formats=["jpg", "jpeg", "bmp", "png", "wsq", "tiff"]

def main(argv):
   in_file = ''
   out_format = ''
   out_file=''
   
   try:
      opts, args = getopt.getopt(argv,"hi:f:o:",["ifile=","ofile=","format="])
   except getopt.GetoptError:
      print 'convert_NIST_finger.py -i <inputfile> -f <format> [-o <outputfile>]'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'convert_NIST_finger.py -i <inputfile> -f <format> [-o <outputfile>]'
         sys.exit(1)
      elif opt in ("-i", "--ifile"):
         in_file = arg
      elif opt in ("-f", "--format"):
         out_format = arg
      elif opt in ("-o", "--ofile"):
         out_file = arg
         
   if(not out_format in valid_image_formats):
      print("Invalid image format "+ out_format)
      sys.exit(1);
   
   
   if(len(in_file)<4 or in_file[len(in_file)-4:]!=".eft"):
      print("Incorrect file format: " + in_file[len(in_file)-4:])
      sys.exit(1)
   dir_path=in_file[0:len(in_file)-4]
   
   if not os.path.isfile(in_file):
      print("file '"+in_file+ "' does not exist!")
      sys.exit(1)

   print("Input file is "+ in_file)
   print("Output format is "+ out_format)
   print("Output file is "+ out_file)

   in_file_name=in_file[max(0, in_file.rfind('/')+1):len(in_file)-4]

   if os.path.exists(dir_path):
      print("Attempting to clean/remove directory "+dir_path)
      shutil.rmtree(dir_path)   
      try:
          os.removedirs(dir_path)
      except:
          pass
      
   #Create output directory if does not exist 
   #(directory removal just attempted so should not exist unless permissions issue)
   if not os.path.exists(dir_path):
      print("Creating directory "+dir_path)
      os.makedirs(dir_path)
   else:   
      print("Directory "+dir_path+" already exists and cannot be removed")
      sys.exit(1)
      
   #Produce NIST formatted field and raw image output   
   print("Running "+nist_path+"an2k2txt "+in_file+ " "+dir_path+"/"+in_file_name+".fmt")
   os.system(nist_path+"an2k2txt "+in_file+ " "+dir_path+"/"+in_file_name+".fmt")   
   
   
   records = {} 
   NFIQs={}
   minutiae={}
   full_records = [] 
   full_values = [] 
   img_x=-1
   img_y=-1

   type_14=0;
   finger_index=-1
   
   #Open txt field file and parse fields/records
   with open(dir_path+"/"+in_file_name+".fmt", 'rw') as fmt_file:
        for line in fmt_file:
            splitLine = line.split('=')
            
            rec_num=(splitLine[0])[:splitLine[0].find("[")-1]              
            field_num=((splitLine[0])[splitLine[0].find("["):]).replace('[','').replace(']','')              
            field_val=(splitLine[1])[:len(splitLine[1])-2]           
            print("Field number is "+field_num +" Record number is "+rec_num +" field value is "+field_val)

            if(field_num in x_dim_fields):
               img_x=int(field_val)
               img_y=-1
               print("Found X-coordinate")
            
            if(field_num in y_dim_fields):
               img_y=int(field_val)
               print("Found Y-coordinate")
            print(splitLine[1:][0])
            new_val=splitLine[1:][0]
            
            if field_num=="14.002" and type_14==1 or field_num=="4.002" and type_14==0:
               finger_index=int(field_val  )
               print("Finger INDEX is "+str(finger_index))
            
            new_val=field_val
            if(".tmp" in splitLine[1:][0]):
               print("Found image file "+splitLine[1:][0])
               splitLine[1:][0]=(splitLine[1:][0]).replace(".tmp", "."+out_format)
               new_val=(splitLine[1:][0]).replace(".tmp", "."+out_format)
               if(img_x!=-1 and img_y!=-1):
                  print("rawtopgm "+str(img_x)+ " "+str(img_y) + " "+ field_val + " > " + field_val[0:len(field_val)-3]+"pgm")   
                  os.system("rawtopgm "+str(img_x)+ " "+str(img_y) +" "+ field_val + " > " + field_val[0:len(field_val)-3]+"pgm")   
                  print("convert -quality 100 "+field_val[0:len(field_val)-3]+"pgm"+ " " + field_val[0:len(field_val)-3]+"jpg")
                  os.system("convert -quality 100 "+field_val[0:len(field_val)-3]+"pgm"+ " " + field_val[0:len(field_val)-3]+"jpg")
                  os.system("convert -quality 100 "+field_val[0:len(field_val)-3]+"pgm"+ " " + field_val[0:len(field_val)-3]+out_format)

                  #Extract minutiae and orientation flow information
                  os.system(nist_path+"mindtct  -b  -m1 "+field_val[0:len(field_val)-3]+"jpg" +" "+field_val[0:len(field_val)-4]) 
                  minutiae[field_val[0:len(field_val)-4]]=getMinutiae("", field_val[0:len(field_val)-4])

                  #Extract NFIQ score
                  proc = subprocess.Popen([nist_path+"nfiq -d "+ field_val[0:len(field_val)-3]+"jpg" ], stdout=subprocess.PIPE, shell=True)
                  (nfiq, err) = proc.communicate()
                  
                  #valid and unused finger index: so add NFIQ dictionary
                  if finger_index > -1 and finger_index not in NFIQs.keys():
                     print("NFIQ is "+nfiq)
                     print("Finger index is "+str(finger_index))
                     NFIQs[finger_index]=int(nfiq[0:len(nfiq)-1])
                      
                  
                  img_x=-1
                  img_y=-1
#                  os.system("mv "+ field_val[0:len(field_val)-3]+out_format+ " "+dir_path+"/" )   
               
            records[field_num] = {"field":field_val, "value":new_val}
#            full_records[splitLine[0]] = ",".join(splitLine[1:])
#            full_records[splitLine[0]] = ",".join([new_val])
            full_records.append(splitLine[0])

            
            #Test to see if Type 4 or 14 record
            if field_num=="1.003":
               if field_val=="14":
                  type_14=1
                  print("Type 14 record detected") 
               elif field_val=="4":
                  type_14=0
                  print("Type 4 record detected") 


            full_values.append(new_val)

        fmt_file.close()
        
   with open(dir_path+"/"+in_file_name+".new.fmt", 'w') as fmt_out_file:
  #      for key, value in full_records.iteritems():
#        for key in sorted(full_records):
#             print(key+"="+value)         
         for i in range(0,len(full_records)):
            fmt_out_file.write(full_records[i]+"="+full_values[i])


   
   if out_file !='':         
      os.system(nist_path+"txt2an2k "+dir_path+"/"+in_file_name+".new.fmt" +" "+out_file) 
      print(nist_path+"txt2an2k "+dir_path+"/"+in_file_name+".new.fmt" +" "+out_file)
   else:         
      os.system(nist_path+"txt2an2k "+dir_path+"/"+in_file_name+".new.fmt" +" "+"new.eft") 
      print(nist_path+"txt2an2k "+dir_path+"/"+in_file_name+".new.fmt" +" "+"new.eft")
   

   #Cleanup images      
   os.system("rm *.pgm")
   os.system("rm *.tmp")
   os.system("mv *.jpg" +" "+dir_path+"/" )
   os.system("mv *.brw" +" "+dir_path+"/" )
   os.system("mv *.hcm" +" "+dir_path+"/" )
   os.system("mv *.lcm" +" "+dir_path+"/" )
   os.system("mv *.xyt" +" "+dir_path+"/" )
   os.system("mv *.min" +" "+dir_path+"/" )
   os.system("mv *.dm" +" "+dir_path+"/" )
   os.system("mv *.qm" +" "+dir_path+"/" )
   os.system("mv *.lfm" +" "+dir_path+"/" )
#   os.system("mv *.nfiq" +" "+dir_path+"/" )
   os.system("mv *."+out_format +" "+dir_path+"/" )

   if (not '1.5.1.1 [1.005]' in full_records) and type_14==0:
      print("TEST FAILED. Missing date field 1.005")      
#      print records.keys();
   elif (not "11.2.1.1 [14.002]" in full_records) and type_14==1:
      print("TEST FAILED. Missing IDC field 14.002")
   else:
      print("TEST PASSED")
   print NFIQs
   json_dict={"NFIQ":NFIQs, "Records": records, "Minutiae": minutiae, "Type 1 Def":record_type_1_to_map, 
              "Type 2 Def":record_type_1_to_map, "Type 14 Def":record_type_1_to_map,
              "Type 14 Def":record_type_1_to_map}

   with open(dir_path + '/'+'json.txt', 'w') as outfile:
        json.dump(json_dict, outfile)
   

      
#print sys.argv[1:]   
main(sys.argv[1:])   


