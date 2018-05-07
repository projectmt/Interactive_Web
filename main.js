function renderDropdown() {
    Plotly.d3.json('/names', function(error, data){
        if (error) return console.warn(error);

        selectElem = d3.select('#sampleChoices');

        selectElem.selectAll('option')
            .data(data)
            .enter()
            .append('option')
            .attr('value',function(d){return d;})
            .text(function(d){return d;});
    });
};

function createPieChart(trace, id, restyle) {

    if (restyle) {
        Plotly.restyle('pie', trace);
    }

    var trace1 = {
        values: trace.values,
        labels: trace.labels,
        text: trace.desc,
        textinfo: 'percent',
        hoverinfo: 'label+text+value',
        type: 'pie'
    }

    var data = [trace1];
    var layout = {
        title: id +': Top 10 OTU Microbiomes',
        legend: {"orientation": "h"}
    };

    Plotly.newPlot('pie',data,layout)
}

function createBubblePlot(trace, id, restyle) {
    if (restyle) {
        Plotly.restyle('bubble', trace);
    };

    var trace1 = {
        x: trace.x,
        y: trace.y,
        mode: 'markers',
        text: trace.desc,
        hoverinfo: "x+y+text",
        marker: {
            size: trace.marker.size,
            color: trace.x
            }
    };

    var data = [trace1];

    var layout = {
        title: id + ': OTU Volume and Spread',
        showlegend: false
        };

    Plotly.newPlot('bubble', data, layout);
};

function populateMetadata(sample) {
    metaURL = '/metadata/' + sample
    Plotly.d3.json(metaURL, function(error, data){
        if (error) return console.warn(error);

        var details = new Array;

        for (var key in data) {
            details.push(key+': '+data[key]);
        };

        selectElem = d3.select('#metadataInfo');
        selectElem.html('');

        selectElem.selectAll('p')
            .data(details)
            .enter()
            .append('p')
            .attr('class','metaDetails')
            .text(function(d){return d;});
    });
};

function pullPieData(sample, restyle){
    sampleURL = '/samples/' + sample;

    Plotly.d3.json(sampleURL, function(error, data){
        if (error) return console.warn(error);

        var trace = {
            values: data.sample_values.slice(0,10),
            labels: data.otu_ids.slice(0,10),
            desc: data.descriptions.slice(0,10)
        };

        if (restyle) {createPieChart(trace, data.id, true);};

        createPieChart(trace, data.id);
    });
}

function pullBubbleData(sample, restyle){
    sampleURL = '/samples/' + sample;

    Plotly.d3.json(sampleURL, function(error, data){
        if (error) return console.warn(error);

        var trace = {
            x: data.otu_ids,
            y: data.sample_values,
            marker: {
                size: data.sample_values,
            },
            desc: data.descriptions
        }

        if (restyle) {createBubblePlot(trace, data.id, true);};

        createBubblePlot(trace, data.id);
    });
}

function optionChanged(dataset) {
    pullPieData(dataset,true);
    pullBubbleData(dataset,true);
    populateMetadata(dataset);
};


renderDropdown();
pullPieData('BB_940');
pullBubbleData('BB_940');
populateMetadata('BB_940');
