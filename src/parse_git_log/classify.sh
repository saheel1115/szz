PROJ="/biodata/ec_data/projects/"
#PROJ="test"
ORIG_LOG_DIR="orig_logs"

##1. dump log 
python dump_log.py $PROJ

#2. parse_log: this step categorizes logs into bug/not bug based on regular expression search
#
python parse_logs.py -i $PROJ -d $ORIG_LOG_DIR --all   #dump all logs in xml format

#3. dump the original logs
python dump_db.py -p orig_logs/ --conf config.ini -v d --log log.txt
