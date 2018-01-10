    ID_TO_NAME = {};
    NAME_TO_ID = {};
    ID_TO_VOTES = {};
    NODES = [];

    RANKS = [];

    function calc(nodes, cb) {
        //nodes = [[1,2],[],[0,1,4],[4,5],[3,5],[3]]
        linkProb = 0.85 //high numbers are more stable
        tolerance = 0.0001 //sensitivity for accuracy of convergence. 

        console.log(nodes);

        PR = new Pagerank(nodes, linkProb, tolerance, function(err, res) {
            RESULT = res;
            
            $.each(RESULT, function(id, val) {
                var abs_score = parseInt(val * 100000);
                var rel_score = parseInt(val * 100000 / (ID_TO_VOTES[id] + 1));
                var score = parseInt(val * 100000 / Math.log2(ID_TO_VOTES[id] + 2));
            
                RANKS.push([score, rel_score, abs_score, id]);
            
            })
            
            RANKS.sort(function(a, b) {
                return a[0] < b[0] ? 1 : -1;
            });

            console.log(RANKS);
            
            if (cb) {
                cb();
            }
            
        });
        
        PR.startRanking();
                
    }

    function render() {
        $.each(RANKS, function(id, rank) {
        
            $(".rank-container table").append("<tr><td>" + rank[0] + "</td><td>" + rank[1] + "</td><td>" + rank[2] + "</td><td>" + ID_TO_NAME[rank[3]] + "</td></tr>");
            
        })        
    }
    function run(cb) {
        $.getJSON("/misc/yours/data.json", function(data) {
            $.each(data.nodes, function(id, node) {
                NAME_TO_ID[node.caption] = null;
            })

            var count = 0;
            $.each(NAME_TO_ID, function(name, id) {
                NAME_TO_ID[name] = count;
                ID_TO_VOTES[count] = 0;
                ID_TO_NAME[count] = name;
                NODES.push([
                    NAME_TO_ID["clemens"], 
                    NAME_TO_ID["codemojo"],
                    NAME_TO_ID["ero"], 
                    NAME_TO_ID["creative.mind"], 
                    NAME_TO_ID["bend0ver"],
                    NAME_TO_ID["mooncryption"], 
                    NAME_TO_ID["txcsh"], 
                ]);
                //NODES.push([NAME_TO_ID["Ryan X. Charles"], NAME_TO_ID["clemens"]]);
                //NODES.push([]);
                count++;
            })
            
            $.each(data.edges, function(id, edge) {
                ID_TO_VOTES[NAME_TO_ID[edge.target]]++;
                NODES[NAME_TO_ID[edge.source]].push(NAME_TO_ID[edge.target]);
            })
            
            calc(NODES, cb);
        })        
    }
