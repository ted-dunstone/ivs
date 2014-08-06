


#########################################################
#Hub side

#Start the hub receiver for exchange Australia_NZ_Exchange 
python hub_receiver.py -i Australia_NZ_Exchange


#Start the hub transformer (for all exchanges).
python hub_transformer.py -i Australia_NZ_Exchange





#########################################################
#Australia_NZ Agency side


#Start the AFIS handler
python matcher.py -i Australia_NZ_Exchange







#########################################################
#Thailand Agency side

#Start the AFIS match result (from other agency) listener 
python match_listener.py -i Thailand_Exchange

#Send the request to the Australia_NZ AFIS
python send_msg.py -i Thailand_Exchange -q Australia_NZ_Exchange -t match -p 1 


