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


#define X-Y coordinate NIST fields
x_dim_fields=["3.6.1.1", "4.6.1.1", "5.6.1.1", "6.6.1.1",
                 "7.6.1.1", "8.6.1.1", "9.6.1.1", "10.6.1.1", "11.6.1.1", "12.6.1.1",]
                 
y_dim_fields=["3.7.1.1", "4.7.1.1", "5.7.1.1", "6.7.1.1",
                 "7.7.1.1", "8.7.1.1", "9.7.1.1", "10.7.1.1", "11.7.1.1", "12.7.1.1",]


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

   if os.path.exists(dir_path):
   #   os.removedirs(dir_path)
      shutil.rmtree(dir_path)   
      
   #Create output directory if does not exist 
   #(directory removal just attempted so should not exist unless permissions issue)
   if not os.path.exists(dir_path):
      print("Creating directory "+dir_path)
      os.makedirs(dir_path)
   else:   
      print("Directory "+dir_path+" already exists and cannot be removed")
      sys.exit(1)
      
   #Produce NIST formatted field and raw image output   
   print("Running "+"an2k2txt "+in_file+ " "+dir_path+"/"+in_file[0:len(in_file)-4]+".fmt")
   os.system("an2k2txt "+in_file+ " "+dir_path+"/"+in_file[0:len(in_file)-4]+".fmt")   
   
   
   #Read the text file into a list
   records = {} 
   full_records = [] 
   full_values = [] 
   img_x=-1
   img_y=-1
   
   #Open txt field file and parse fields/records
   with open(dir_path+"/"+in_file[0:len(in_file)-4]+".fmt", 'rw') as fmt_file:
        for line in fmt_file:
            splitLine = line.split('=')
            
            field_num=(splitLine[0])[:splitLine[0].find("[")-1]              
            rec_num=(splitLine[0])[splitLine[0].find("["):]              
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
                  img_x=-1
                  img_y=-1
#                  os.system("mv "+ field_val[0:len(field_val)-3]+out_format+ " "+dir_path+"/" )   
               
            records[field_num] = ",".join(field_val)
#            full_records[splitLine[0]] = ",".join(splitLine[1:])
#            full_records[splitLine[0]] = ",".join([new_val])
            full_records.append(splitLine[0])
            full_values.append(new_val)
        fmt_file.close()
        
   with open(dir_path+"/"+in_file[0:len(in_file)-4]+".new.fmt", 'w') as fmt_out_file:
  #      for key, value in full_records.iteritems():
#        for key in sorted(full_records):
#             print(key+"="+value)         
         for i in range(0,len(full_records)):
            fmt_out_file.write(full_records[i]+"="+full_values[i])


   
   if out_file !='':         
      os.system("txt2an2k "+dir_path+"/"+in_file[0:len(in_file)-4]+".new.fmt" +" "+out_file) 
      print("txt2an2k "+dir_path+"/"+in_file[0:len(in_file)-4]+".new.fmt" +" "+out_file)
   else:         
      os.system("txt2an2k "+dir_path+"/"+in_file[0:len(in_file)-4]+".new.fmt" +" "+"new.eft") 
      print("txt2an2k "+dir_path+"/"+in_file[0:len(in_file)-4]+".new.fmt" +" "+"new.eft")
   

   #Cleanup images      
   os.system("rm *.pgm")
   os.system("rm *.tmp")
   os.system("mv *.jpg" +" "+dir_path+"/" )
   os.system("mv *."+out_format +" "+dir_path+"/" )

   if not '1.005' in records.keys():
      print("TEST FAILED. Missing date field 1.005")      
#      print records.keys();
   elif not '14.002' in records.keys():
      print("TEST FAILED. Missing IDC field 14.002")
   else:
      print("TEST PASSED")



      
#print sys.argv[1:]   
main(sys.argv[1:])   


