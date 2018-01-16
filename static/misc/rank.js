    WITNESSES = {
        "Ryan X. Charles": true,
        "clemens": true, 
    }

    LINK_PROB = 0.85;
    TOLERANCE = 0.0001;

    DATA = {};

    ID_TO_NAME = {};
    NAME_TO_ID = {};
    ID_TO_VOTES = {};
    ID_TO_OUT_VOTES = {};
    NODES = [];

    RANKS = {};
    RANK_LIST = [];

    TOTAL_VOTES = 0;
    MAX_VOTES = 0;
    AVG_VOTES = 0;

    MAX_RANK = 0;

    RANK_MULTIPLIER = 1000;

    /* http://www.ollysco.de/2012/04/gaussian-normal-functions-in-javascript.html */
    Math.getGaussianFunction = function(mean, standardDeviation, maxHeight) {
        return function getNormal(votes) {
            var x = votes / MAX_VOTES;
            return maxHeight * Math.pow(Math.E, -Math.pow(x - mean, 2) / (2 * (standardDeviation * standardDeviation)));
        }
    };    

    get_normal = Math.getGaussianFunction(0.0, 1.0, 100);    

    function calc_stats() {
        $.each(NAME_TO_ID, function(name, id) {
            TOTAL_VOTES += ID_TO_VOTES[id];
            if (ID_TO_VOTES[id] > MAX_VOTES) {
                MAX_VOTES = ID_TO_VOTES[id];
            }
        })
        AVG_VOTES = TOTAL_VOTES / Object.keys(NAME_TO_ID).length;
    }

    function prepare(data) {
        NAME_TO_ID = {};
        ID_TO_NAME = {};
        ID_TO_VOTES = {};
        ID_TO_OUT_VOTES = {};
        NODES = [];
        
        $.each(WITNESSES, function(name, yes) {
            NAME_TO_ID[name] = null;
        })
        $.each(data.nodes, function(id, node) {
            NAME_TO_ID[node.caption] = null;
        })
        $.each(data.edges, function(id, edge) {
            NAME_TO_ID[edge.source] = null;
            NAME_TO_ID[edge.target] = null;
        })

        var count = 0;
        $.each(NAME_TO_ID, function(name, id) {
            NAME_TO_ID[name] = count;
            ID_TO_NAME[count] = name;
            count++;
        })

        $.each(NAME_TO_ID, function(name, id) {            
            ID_TO_VOTES[id] = 0;
            ID_TO_OUT_VOTES[id] = 0;
            if (WITNESSES[name]) {
                ID_TO_VOTES[id] += Object.keys(NAME_TO_ID).length;
            }
            NODES.push([]);
            $.each(WITNESSES, function(witness_name, foo) {
                NODES[NODES.length - 1].push(NAME_TO_ID[witness_name])
            })                
        })
        
        $.each(data.edges, function(id, edge) {
            ID_TO_VOTES[NAME_TO_ID[edge.target]]++;
            ID_TO_OUT_VOTES[NAME_TO_ID[edge.source]]++;
            NODES[NAME_TO_ID[edge.source]].push(NAME_TO_ID[edge.target]);
        })    
    }

    function update_with_flow(ranks) {
        $.each(ranks, function(id, data) {
            if (data.rank > MAX_RANK) {
                MAX_RANK = data.rank
            }
        })
        $.each(ranks, function(id, data) {
            data.flow = parseInt(data.rank * 10 / MAX_RANK);
        })
    }


    function calc_weight(data) {
        return parseInt(get_normal(data.votes_in));
    }

    function calc(data, cb) {
        //nodes = [[1,2],[],[0,1,4],[4,5],[3,5],[3]]
        var linkProb = LINK_PROB; //high numbers are more stable
        var tolerance = TOLERANCE; //sensitivity for accuracy of convergence. 

        prepare(data);
        nodes = NODES;

        //console.log(nodes);
        
        RANKS = {};
        PR = new Pagerank(nodes, linkProb, tolerance, function(err, res) {
            RESULT = res;

            calc_stats();
            
            $.each(RESULT, function(id, val) {
                RANKS[id] = {id: id};
                RANKS[id].name = ID_TO_NAME[id];
                RANKS[id].rank_abs = parseInt(val * RANK_MULTIPLIER);
                RANKS[id].rank_rel = parseInt(val * RANK_MULTIPLIER / (ID_TO_VOTES[id] + 1));
                RANKS[id].rank_log2 = parseInt(val * RANK_MULTIPLIER / Math.log2(ID_TO_VOTES[id] + 2));                
                RANKS[id].votes_out = ID_TO_OUT_VOTES[id];                
                RANKS[id].votes_in = ID_TO_VOTES[id];
                RANKS[id].weight = calc_weight(RANKS[id]);
                RANKS[id].rank = RANKS[id].weight * RANKS[id].rank_abs;
            })
            
            update_with_flow(RANKS);
            
            RANK_LIST = Object.values(RANKS);
            
            RANK_LIST.sort(function(a, b) {
                return a[0] < b[0] ? 1 : -1;
            });

            if (cb) {
                cb();
            }
            
        });
        
        PR.startRanking();                
    }

    function render_gauss() {
        //$.plot($(".gauss-container"), [ [[0, 0], [1, 1]] ], { yaxis: { max: 1 } });    

        var data = [];
        for (var i=0; i<MAX_VOTES+1; i++) {
            data.push([i, get_normal(i)]);
        }
        $.plot($(".gauss-container"), [ data ]);    
        
    }

    function render() {
        render_gauss();
    
        $(".rank-container table tbody").html("");
        $.each(RANK_LIST, function(id, rank) {
        
            $(".rank-container table tbody").append("<tr><td>"
                + rank.flow + "</td><td>"
                + rank.rank + "</td><td>"
                + rank.weight + "</td><td>"
                + rank.votes_in + "</td><td>"
                + rank.votes_out + "</td><td>"
                + rank.rank_log2 + "</td><td>"
                + rank.rank_rel + "</td><td>"
                + rank.rank_abs + "</td><td>"
                + rank.name + "</td></tr>"
            );
        })

        $(".rank-container table").dataTable({"order": [[ 0, "desc" ]]});
    }
    function run(cb) {
        $.getJSON("/misc/yours/data.json", function(data) {
            DATA = data;
            
            calc(data, cb);
        })        
    }
    
