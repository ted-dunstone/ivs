


#########################################################
#Hub side

python hub_master.py -e Australia_NZ_Exchange:Australia_Exchange:NZ_Exchange


#########################################################
#Australia_NZ Agency side

#Start the AFIS handler
python  match_master.py -a Australia_NZ  -e Australia_NZ_Exchange:Australia_Exchange:NZ_Exchange 

#########################################################
#Thailand Agency side

#Start the AFIS match result (from other agency) listener 
python match_listener.py -e Thailand_Exchange

#Send the request to the Australia_NZ AFIS
python send_msg.py -i Thailand_Exchange -q Australia_NZ_Exchange -t match -p 1 


