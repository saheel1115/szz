
extn2tag = { '.c' : 'c', \
        '.cpp' : 'cpp', '.cpp_' : 'cpp', '.cpp1' : 'cpp', '.cpp2' : 'cpp', '.cppclean' : 'cpp', '.cpp_NvidiaAPI_sample' : 'cpp', '.cpp-s8inyu' : 'cpp', '.cpp-woains' : 'cpp', \
        '.cs' : 'csharp', '.csharp' : 'csharp',  \
        '.m' : 'objc', \
        '.java' : 'java', \
        '.scala' : 'scala', '.scla' : 'scala', \
        '.go' : 'go', \
        '.javascript' : 'javascript', '.js' : 'javascript', \
        '.coffee' : 'coffeescript', '.coffeescript' : 'coffeescript', \
        '.ts' : 'typescript', '.typescript' : 'typescript', \
        '.rb'  : 'ruby', \
        '.php' : 'php', \
        '.pl' : 'perl', \
        '.py' : 'python', \
        '.sh' : 'shell', '.SH' : 'shell', '.ksh' : 'shell', '.bash' : 'shell', '.bat' : 'shell',  '.bats' : 'shell', \
        '.cljx' : 'clojure', '.cljscm' : 'clojure', '.clj' : 'clojure', '.cljc': 'clojure', '.cljs' : 'clojure', \
        '.css' : 'css', \
        '.erl' : 'erlang', \
        '.hs' : 'haskell'
        }

bug_type_root = {
        'ALGO'        : "algorithm",
        'CONCURRANCY' : " multi thread | multi process | multithread | multiprocess |  multi-thread | multi-process | race | deadlock | synchronize",
        'MEMORY'      : "memory leak | buffer overflow | null pointer | dangling pointer | heap overflow | double free | memory corruption | segmentation fault ",
        'PROGRAMMING' : "missing switch | control flow | exception handl | template | field | method | class | derived | implement | call | parsing | parse | namespace | " \
                + "copy | paste | clone | refactor | merge | " \
                + "cast | type | integer | float | int | character | overload | initializ | reference | reflect | array | " \
                + "indent | formatting | " \
                + "initializ | default value | " \
                + "typo | " \
                + "compile | build "
        }


bug_type_impact = {
        'SECURITY'    : "security | secure | vulnerability | vulnerable | malicious | attack | ssl | sandbox | remote code | auth | password",
        'PERFORMANCE' : "performance | slow | delay | optimization | optimize",
        'CRASH'       : "crash | halt | hang | reboot | restart | stop responding | not working | not responding "
        }

bug_type_comp = {
        'CORE'        : "kernel | vm | core | system | env",
        'GUI'         : "gui | user interface | screen | touch | progress bar | display | view",
        'NETWORK'     : "network | packet | tcp | socket | http",
        'IO'          : "i/o | disk"
        }

