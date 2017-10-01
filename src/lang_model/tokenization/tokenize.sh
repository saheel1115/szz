#echo "python src/lang_model/tokenization/tokenize.py -p /biodata/ec_data/snapshots/$1 -l java --reverse --append >$1.out1 2>$1.err1"
#python src/lang_model/tokenization/tokenize.py -p /biodata/ec_data/snapshots/$1 -l java --reverse --append >$1.out1 2>$1.err1
echo "python mapLines.py -p /biodata/ec_data/snapshots/$1 >$1.out1 2>$1.err1"
python mapLines.py -p /biodata/ec_data/snapshots/$1 >$1.out1 2>$1.err1

echo "python mergeEntropies.py -n atmosphere -p /biodata/ec_data/snapshots/$1/ -l java > $1.out 2>$1.err"
python mergeEntropies.py -n atmosphere -p /biodata/ec_data/snapshots/$1/ -l java > $1.out 2>$1.err
