echo "=============  qpid  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/qpid -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > qpid.out 2> qpid.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/qpid -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > qpid_r.out 2> qpid_r.err &
echo "=============  derby  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/derby -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > derby.out 2> derby.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/derby -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > derby_r.out 2> derby_r.err &
echo "=============  lucene  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/lucene -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > lucene.out 2> lucene.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/lucene -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > lucene_r.out 2> lucene_r.err &
echo "=============  facebook-android-sdk  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/facebook-android-sdk -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > facebook-android-sdk.out 2> facebook-android-sdk.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/facebook-android-sdk -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > facebook-android-sdk_r.out 2> facebook-android-sdk_r.err &
echo "=============  wicket  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/wicket -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > wicket.out 2> wicket.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/wicket -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > wicket_r.out 2> wicket_r.err &
echo "=============  presto  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/presto -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > presto.out 2> presto.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/presto -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > presto_r.out 2> presto_r.err &
echo "=============  elasticsearch  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/elasticsearch -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > elasticsearch.out 2> elasticsearch.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/elasticsearch -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > elasticsearch_r.out 2> elasticsearch_r.err &
echo "=============  atmosphere  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/atmosphere -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > atmosphere.out 2> atmosphere.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/atmosphere -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > atmosphere_r.out 2> atmosphere_r.err &
echo "=============  netty  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/netty -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > netty.out 2> netty.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/netty -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > netty_r.out 2> netty_r.err &
echo "=============  openjpa  ============="
#nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/openjpa -d /biodata/ec_data/result/entropy --snapshot --append  -b 0 -c 4 > openjpa.out 2> openjpa.err &
nohup python get_cross_entropy_thread.py -p /biodata/ec_data/snapshots/openjpa -d /biodata/ec_data/result/entropy --snapshot --reverse --append  -b 0 -c 4 > openjpa_r.out 2> openjpa_r.err &
