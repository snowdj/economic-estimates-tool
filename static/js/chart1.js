function make_chart(measure, measureType) {

    function convertNumbers(row) {
        var r = {};
        for (var k in row) {
            r[k] = +row[k];
            if (isNaN(r[k])) {
                r[k] = row[k];
            }
        }
        return r;
    }
    d3.csv("/static/data/ee_agg_no_region.csv", convertNumbers, function (data) {
        // convert from long to wide
        var wide = d3.nest()
            .key(function (d) { return d["Year"] }) // sort by key
            .rollup(function (d) { // do this to each grouping
                // reduce takes a list and returns one value
                // in this case, the list is all the grouped elements
                // and the final value is an object with keys
                return d.reduce(function (prev, curr) {
                    prev["Year"] = curr["Year"];
                    prev[curr["Sector"]] = curr[measure];
                    return prev;
                }, {});
            })
            .entries(data) // tell it what data to process
            .map(function (d) { // pull out only the values
                return d.value;
            });


        // remove any entries equal to zero
        // var final
        const sumValues = obj => Object.values(obj).reduce((a, b) => a + b);
        var newwide = wide.filter(function (value, index, arr) {
            // console.log(value.Year);
            copy = JSON.parse(JSON.stringify(value));
            delete copy.Year;
            // console.log(value);
            // console.log(sumValues(value));
            return sumValues(copy) > 0;
        });

        // create indexed data
        indexed = []
        newwide.forEach(function (entry, index) {
            myrow = JSON.parse(JSON.stringify(entry));
            sectors = JSON.parse(JSON.stringify(entry));
            delete sectors.Year;
            if (index == 0) {
                first = JSON.parse(JSON.stringify(entry));
            }
            if (index == 0) {
                for (var i in sectors) {
                    myrow[i] = 100;
                }
            } else {
                for (var i in sectors) {
                    myrow[i] = 100 * sectors[i] / first[i];
                } 
            }
            indexed.push(myrow);
        });

        // create percuk data
        percuk = []
        newwide.forEach(function (entry, index) {
            myrow = JSON.parse(JSON.stringify(entry));
            sectors = JSON.parse(JSON.stringify(entry));
            delete sectors.Year;
            for (var i in sectors) {
                myrow[i] = 100 * sectors[i] / sectors['UK'];
            }
            delete myrow.UK;
            percuk.push(myrow);
        });

        
        if (measureType == "indexed") {
            newwide = JSON.parse(JSON.stringify(indexed));
        } else if (measureType == "percuk") {
            newwide = JSON.parse(JSON.stringify(percuk));
        } else {
            newwide = JSON.parse(JSON.stringify(newwide));
        }
        
        
        // console.log(newwide);
        var chartSeries = ["UK", "All DCMS Sectors", "Creative Industries", "Cultural Sector", "Digital Sector", "Gambling", "Sport", "Telecoms"];
        var ymin = 0;
        if (measureType == "percuk") {
            chartSeries.shift();
        } else if (measureType == "indexed") {
            if (measure == "Imports" | measure == "Exports") {
                ymin = 0;
            } else {
                ymin = 80;
            }
        }
        var chart = c3.generate({
            bindto: '#chart',
            data: {
                json: newwide,
                keys: {
                    x: 'Year', // it's possible to specify 'x' when category axis
                    value: chartSeries,
                },
            },
            axis: {
                y: {
                    tick: {
                        outer: false
                    },
                    padding: {
                        top: 50,
                        bottom: 0
                    },
                    min: ymin
                },
                x: {
                    tick: {
                        culling: false,
                        outer: false
                    },
                    padding: {
                        left: 0.5,
                        right: 0.5
                    }
                }
            },
            legend: {
                // amount of padding to put between each legend element
                padding: 5,
                position: 'right',
                // define custom height and width for the legend item tile
                item: {
                    tile: {
                        width: 15,
                        height: 2
                    }
                }
            },
            size: {
                width: 640,
                height: 500
            },
            padding: {
                top: 10,
                right: 200,
                bottom: 20,
                left: 50,
            },
            grid: {
                x: {
                },
                y: {
                    show: true
                }
            },
            tooltip: {
                format: {
                    // title: function (d) { return 'Data ' + d; },
                    value: function (value, ratio, id) {
                        var format = d3.format(',');
                        return format(value.toFixed(1));
                    }
                    //            value: d3.format(',') // apply this format to both y and y2
                }
            }
        });
        
        if (measureType == "actual") {
            chart.hide('All DCMS Sectors', { withLegend: false });
            chart.hide('UK', { withLegend: false });
        }
    });
}

make_chart("GVA", measureType="actual");



var rad = document.tsChartMeasureTypes.tsMeasure;
var prev = null;
for(var i = 0; i < rad.length; i++) {
    rad[i].addEventListener('change', function() {
        if(this !== prev) {
            prev = this;
        }
        var radval = this.value;
        make_chart(select.value, measureType=radval);
    });
}

var select = document.getElementById("chart-opts");
select.addEventListener("change", update_chart);

function update_chart() {
    var rad = document.tsChartMeasureTypes.tsMeasure;
    var radval = rad.value;
    make_chart(select.value, measureType=radval);
}
