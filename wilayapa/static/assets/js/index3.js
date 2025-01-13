$(function() {
	"use strict";


// chart 1
// Obtenemos el elemento que tiene el atributo 'data-revenue'
var revenueDataElement = document.getElementById('chart1');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var cantidadVentas = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
var options = {
	series: [{
		name: "Total Orders",
		data: cantidadVentas
	}],
	chart: {
		type: "line",
		//width: 100%,
		height: 30,
		toolbar: {
			show: !1
		},
		zoom: {
			enabled: !1
		},
		dropShadow: {
			enabled: 0,
			top: 3,
			left: 14,
			blur: 4,
			opacity: .12,
			color: "#e72e7a"
		},
		sparkline: {
			enabled: !0
		}
	},
	markers: {
		size: 0,
		colors: ["#e72e7a"],
		strokeColors: "#fff",
		strokeWidth: 2,
		hover: {
			size: 7
		}
	},
	plotOptions: {
		bar: {
			horizontal: !1,
			columnWidth: "35%",
			endingShape: "rounded"
		}
	},
	dataLabels: {
		enabled: !1
	},
	stroke: {
		show: !0,
		width: 2.5,
		curve: "smooth"
	},
	colors: ["#e72e7a"],
	xaxis: {
		categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	},
	fill: {
		opacity: 1
	},
	tooltip: {
		theme: "dark",
		fixed: {
			enabled: !1
		},
		x: {
			show: !1
		},
		y: {
			title: {
				formatter: function(e) {
					return ""
				}
			}
		},
		marker: {
			show: !1
		}
	}
  };

  var chart = new ApexCharts(document.querySelector("#chart1"), options);
  chart.render();



// chart 2
var revenueDataElement = document.getElementById('chart2');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var sumaVentas = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
var options = {
	series: [{
		name: "Total Views",
		data: sumaVentas
	}],
	chart: {
		type: "bar",
		//width: 100%,
		height: 30,
		toolbar: {
			show: !1
		},
		zoom: {
			enabled: !1
		},
		dropShadow: {
			enabled: 0,
			top: 3,
			left: 14,
			blur: 4,
			opacity: .12,
			color: "#3461ff"
		},
		sparkline: {
			enabled: !0
		}
	},
	markers: {
		size: 0,
		colors: ["#3461ff"],
		strokeColors: "#fff",
		strokeWidth: 2,
		hover: {
			size: 7
		}
	},
	plotOptions: {
		bar: {
			horizontal: !1,
			columnWidth: "35%",
			endingShape: "rounded"
		}
	},
	dataLabels: {
		enabled: !1
	},
	stroke: {
		show: !0,
		width: 2.5,
		curve: "smooth"
	},
	colors: ["#3461ff"],
	xaxis: {
		categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	},
	fill: {
		opacity: 1
	},
	tooltip: {
		theme: "dark",
		fixed: {
			enabled: !1
		},
		x: {
			show: !1
		},
		y: {
			title: {
				formatter: function(e) {
					return ""
				}
			}
		},
		marker: {
			show: !1
		}
	}
  };

  var chart = new ApexCharts(document.querySelector("#chart2"), options);
  chart.render();



// chart 3
var revenueDataElement = document.getElementById('chart3');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var cantidadPedido = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
var options = {
	series: [{
		name: "Revenue",
		data: cantidadPedido
	}],
	chart: {
		type: "line",
		//width: 100%,
		height: 30,
		toolbar: {
			show: !1
		},
		zoom: {
			enabled: !1
		},
		dropShadow: {
			enabled: 0,
			top: 3,
			left: 14,
			blur: 4,
			opacity: .12,
			color: "#12bf24"
		},
		sparkline: {
			enabled: !0
		}
	},
	markers: {
		size: 0,
		colors: ["#12bf24"],
		strokeColors: "#fff",
		strokeWidth: 2,
		hover: {
			size: 7
		}
	},
	plotOptions: {
		bar: {
			horizontal: !1,
			columnWidth: "35%",
			endingShape: "rounded"
		}
	},
	dataLabels: {
		enabled: !1
	},
	stroke: {
		show: !0,
		width: 2.5,
		curve: "smooth"
	},
	colors: ["#12bf24"],
	xaxis: {
		categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	},
	fill: {
		opacity: 1
	},
	tooltip: {
		theme: "dark",
		fixed: {
			enabled: !1
		},
		x: {
			show: !1
		},
		y: {
			title: {
				formatter: function(e) {
					return ""
				}
			}
		},
		marker: {
			show: !1
		}
	}
  };

  var chart = new ApexCharts(document.querySelector("#chart3"), options);
  chart.render();




// chart 4
var revenueDataElement = document.getElementById('chart4');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var sumPedido = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
var options = {
	series: [{
		name: "Customers",
		data: sumPedido
	}],
	chart: {
		type: "bar",
		//width: 100%,
		height: 30,
		toolbar: {
			show: !1
		},
		zoom: {
			enabled: !1
		},
		dropShadow: {
			enabled: 0,
			top: 3,
			left: 14,
			blur: 4,
			opacity: .12,
			color: "#ff6632"
		},
		sparkline: {
			enabled: !0
		}
	},
	markers: {
		size: 0,
		colors: ["#ff6632"],
		strokeColors: "#fff",
		strokeWidth: 2,
		hover: {
			size: 7
		}
	},
	plotOptions: {
		bar: {
			horizontal: !1,
			columnWidth: "35%",
			endingShape: "rounded"
		}
	},
	dataLabels: {
		enabled: !1
	},
	stroke: {
		show: !0,
		width: 2.5,
		curve: "smooth"
	},
	colors: ["#ff6632"],
	xaxis: {
		categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	},
	fill: {
		opacity: 1
	},
	tooltip: {
		theme: "dark",
		fixed: {
			enabled: !1
		},
		x: {
			show: !1
		},
		y: {
			title: {
				formatter: function(e) {
					return ""
				}
			}
		},
		marker: {
			show: !1
		}
	}
  };

  var chart = new ApexCharts(document.querySelector("#chart4"), options);
  chart.render();



// chart 5
// Obtenemos el elemento que tiene el atributo 'data-revenue'
var revenueDataElement = document.getElementById('chart5');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var revenueData = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
console.log(revenueData);
var options = {
    series: [{
        name: "Revenue",
		data: revenueData
    }],
    chart: {
         type: "area",
       // width: 130,
	    stacked: true,
        height: 280,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#3461ff"
        },
        sparkline: {
            enabled: !1
        }
    },
    markers: {
        size: 0,
        colors: ["#3461ff"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "25%",
            //endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: [2.5],
		//colors: ["#3461ff"],
        curve: "smooth"
    },
	fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#3361ff'],
		  inverseColors: false,
		  opacityFrom: 0.7,
		  opacityTo: 0.1,
		 // stops: [0, 100]
		}
	},
	colors: ["#3361ff"],
    xaxis: {
        categories: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    },
	grid:{
		show: true,
		borderColor: 'rgba(66, 59, 116, 0.15)',
	},
	responsive: [
		{
		  breakpoint: 1000,
		  options: {
			chart: {
				type: "area",
			   // width: 130,
				stacked: true,
			}
		  }
		}
	  ],
	legend: {
		show: false
	  },
    tooltip: {
        theme: "dark"        
    }
  };

  var chart = new ApexCharts(document.querySelector("#chart5"), options);
  chart.render();


// chart 5
// Obtenemos el elemento que tiene el atributo 'data-revenue'
var revenueDataElement = document.getElementById('chart15');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var revenueData4 = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
console.log(revenueData);
var options = {
    series: [{
        name: "Revenue",
		data: revenueData4
    }],
    chart: {
         type: "area",
       // width: 130,
	    stacked: true,
        height: 280,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#e72e7a"
        },
        sparkline: {
            enabled: !1
        }
    },
    markers: {
        size: 0,
        colors: ["#e72e7a"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "25%",
            //endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: [2.5],
		//colors: ["#3461ff"],
        curve: "smooth"
    },
	fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#e72e7a'],
		  inverseColors: false,
		  opacityFrom: 0.7,
		  opacityTo: 0.1,
		 // stops: [0, 100]
		}
	},
	colors: ["#e72e7a"],
    xaxis: {
        categories: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    },
	grid:{
		show: true,
		borderColor: 'rgba(66, 59, 116, 0.15)',
	},
	responsive: [
		{
		  breakpoint: 1000,
		  options: {
			chart: {
				type: "area",
			   // width: 130,
				stacked: true,
			}
		  }
		}
	  ],
	legend: {
		show: false
	  },
    tooltip: {
        theme: "dark"        
    }
  };

  

  var chart = new ApexCharts(document.querySelector("#chart15"), options);
  chart.render();








  var revenueDataElement = document.getElementById('chart17');
  
// Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
var revenueData43 = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
console.log(revenueData);
var options = {
    series: [{
        name: "Revenue",
		data: revenueData43
    }],
    chart: {
         type: "area",
       // width: 130,
	    stacked: true,
        height: 280,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#3461ff"
        },
        sparkline: {
            enabled: !1
        }
    },
    markers: {
        size: 0,
        colors: ["#3461ff"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "25%",
            //endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: [2.5],
		//colors: ["#3461ff"],
        curve: "smooth"
    },
	fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#3461ff'],
		  inverseColors: false,
		  opacityFrom: 0.7,
		  opacityTo: 0.1,
		 // stops: [0, 100]
		}
	},
	colors: ["#3461ff"],
    xaxis: {
        categories: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    },
	grid:{
		show: true,
		borderColor: 'rgba(66, 59, 116, 0.15)',
	},
	responsive: [
		{
		  breakpoint: 1000,
		  options: {
			chart: {
				type: "area",
			   // width: 130,
				stacked: true,
			}
		  }
		}
	  ],
	legend: {
		show: false
	  },
    tooltip: {
        theme: "dark"        
    }
  };

  

  var chart = new ApexCharts(document.querySelector("#chart17"), options);
  chart.render();
  // Obtenemos el elemento que tiene el atributo 'data-revenue'
  var revenueDataElement = document.getElementById('chart16');
	
  // Leemos los datos del atributo 'data-revenue' y los convertimos a un objeto JavaScript (array)
  var revenueDat2a = JSON.parse(revenueDataElement.getAttribute('data-revenue'));
  console.log(revenueData);
  var options = {
	  series: [{
		  name: "Revenue",
		  data: revenueDat2a
	  }],
	  chart: {
		   type: "area",
		 // width: 130,
		  stacked: true,
		  height: 280,
		  toolbar: {
			  show: !1
		  },
		  zoom: {
			  enabled: !1
		  },
		  dropShadow: {
			  enabled: 0,
			  top: 3,
			  left: 14,
			  blur: 4,
			  opacity: .12,
			  color: "#e72e7a"
		  },
		  sparkline: {
			  enabled: !1
		  }
	  },
	  markers: {
		  size: 0,
		  colors: ["#e72e7a"],
		  strokeColors: "#fff",
		  strokeWidth: 2,
		  hover: {
			  size: 7
		  }
	  },
	  plotOptions: {
		  bar: {
			  horizontal: !1,
			  columnWidth: "25%",
			  //endingShape: "rounded"
		  }
	  },
	  dataLabels: {
		  enabled: !1
	  },
	  stroke: {
		  show: !0,
		  width: [2.5],
		  //colors: ["#3461ff"],
		  curve: "smooth"
	  },
	  fill: {
		  type: 'gradient',
		  gradient: {
			shade: 'light',
			type: 'vertical',
			shadeIntensity: 0.5,
			gradientToColors: ['#e72e7a'],
			inverseColors: false,
			opacityFrom: 0.7,
			opacityTo: 0.1,
		   // stops: [0, 100]
		  }
	  },
	  colors: ["#e72e7a"],
	  xaxis: {
		  categories: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
	  },
	  grid:{
		  show: true,
		  borderColor: 'rgba(66, 59, 116, 0.15)',
	  },
	  responsive: [
		  {
			breakpoint: 1000,
			options: {
			  chart: {
				  type: "area",
				 // width: 130,
				  stacked: true,
			  }
			}
		  }
		],
	  legend: {
		  show: false
		},
	  tooltip: {
		  theme: "dark"        
	  }
	};
  
	var chart = new ApexCharts(document.querySelector("#chart16"), options);
	chart.render();

// chart6

// Obtener el elemento que tiene el atributo 'data-revenue'
var revenueDataElement = document.getElementById('chart6');

// Leer el atributo 'data-revenue' y convertirlo a un objeto JavaScript (JSON)
var productosPorcentaje = JSON.parse(revenueDataElement.getAttribute('data-revenue'));

// Verifica que los datos sean correctos
console.log(productosPorcentaje);  // Esto debe ser un array de tuplas como [["PRUEBA7", 35.22], ["lanyard", 24.60], ...]

// Extraer los nombres de los productos y los porcentajes para el gráfico
var labels = productosPorcentaje.map(function(item) { return item[0]; });
var data = productosPorcentaje.map(function(item) { return item[1]; });

// Crear el gráfico
var chart = new Chart(document.getElementById('chart6'), {
  type: 'doughnut',
  data: {
    labels: labels,
    datasets: [{
      label: "Top Selling Products",
      backgroundColor: ["#12bf24", "#3461ff", "#ff6632", "#ff9900", "#ff3300"], // Colores para los productos
      data: data
    }]
  },
  options: {
    maintainAspectRatio: false,
    cutoutPercentage: 85,
    responsive: true,
    legend: {
      display: true
    }
  }
});
   // chart 7

   var options = {
	chart: {
	  height: 300,
	  type: 'radialBar',
	  toolbar: {
		show: false
	  }
	},
	plotOptions: {
	  radialBar: {
		//startAngle: -135,
		//endAngle: 225,
		 hollow: {
		  margin: 0,
		  size: '80%',
		  background: 'transparent',
		  image: undefined,
		  imageOffsetX: 0,
		  imageOffsetY: 0,
		  position: 'front',
		  dropShadow: {
			enabled: true,
			top: 3,
			left: 0,
			blur: 4,
			color: 'rgba(0, 169, 255, 0.85)',
			opacity: 0.65
		  }
		},
		track: {
		  background: '#e5d1ff',
		  strokeWidth: '67%',
		  margin: 0, // margin is in pixels
		  dropShadow: {
			enabled: 0,
			top: -3,
			left: 0,
			blur: 4,
			color: 'rgba(0, 169, 255, 0.85)',
			opacity: 0.65
		  }
		},
		dataLabels: { 
		  showOn: 'always',
		  name: {
			offsetY: -20,
			show: true,
			color: '#212529',
			fontSize: '16px'
		  },
		  value: {
			formatter: function (val) {
					  return val + "%";
				  },
			color: '#212529',
			fontSize: '35px',
			show: true,
			offsetY: 10,
		  }
		}
	  }
	},
	fill: {
	  type: 'gradient',
	  gradient: {
		shade: 'light',
		type: 'horizontal',
		shadeIntensity: 0.5,
		gradientToColors: ['#8932ff'],
		inverseColors: false,
		opacityFrom: 1,
		opacityTo: 1,
		stops: [0, 100]
	  }
	},
	colors: ["#8932ff"],
	series: [78],
	stroke: {
	  lineCap: 'round',
	  //dashArray: 4
	},
	labels: ['Total Traffic'],
	responsive: [
		{
		  breakpoint: 1281,
		  options: {
			chart: {
				height: 280,
			}
		  }
		}
	  ],

  }

  var chart = new ApexCharts(
	document.querySelector("#chart7"),
	options
  );

  chart.render();


   
// chart 8

var options = {
    series: [{
        name: "Messages",
        data: [0, 160, 671, 414, 555, 257, 901, 613, 727, 414, 555, 0]
    }],
    chart: {
        type: "area",
        //width: 130,
        height: 55,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#e72e2e"
        },
        sparkline: {
            enabled: !0
        }
    },
    markers: {
        size: 0,
        colors: ["#e72e7a"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "35%",
            endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: 2.5,
        curve: "smooth"
    },
	fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#e72e7a'],
		  inverseColors: false,
		  opacityFrom: 0.6,
		  opacityTo: 0.1,
		  //stops: [0, 100]
		}
	  },
    colors: ["#e72e7a"],
    xaxis: {
        categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    },
	grid:{
		show: false,
		borderColor: 'rgba(66, 59, 116, 0.15)',
	},
    tooltip: {
        theme: "dark",
        fixed: {
            enabled: !1
        },
        x: {
            show: !1
        },
        y: {
            title: {
                formatter: function(e) {
                    return ""
                }
            }
        },
        marker: {
            show: !1
        }
    }
  };

  var chart = new ApexCharts(document.querySelector("#chart8"), options);
  chart.render();


   
// chart 9

var options = {
    series: [{
        name: "Posts",
        data: [0, 160, 671, 414, 555, 257, 901, 613, 727, 414, 555, 0]
    }],
    chart: {
        type: "area",
        //width: 130,
        height: 55,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#12bf24"
        },
        sparkline: {
            enabled: !0
        }
    },
    markers: {
        size: 0,
        colors: ["#3461ff"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "35%",
            endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: 2.5,
        curve: "smooth"
    },
    fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#12bf24'],
		  inverseColors: false,
		  opacityFrom: 0.6,
		  opacityTo: 0.1,
		  //stops: [0, 100]
		}
	  },
    colors: ["#12bf24"],
    xaxis: {
        categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    },
    tooltip: {
        theme: "dark",
        fixed: {
            enabled: !1
        },
        x: {
            show: !1
        },
        y: {
            title: {
                formatter: function(e) {
                    return ""
                }
            }
        },
        marker: {
            show: !1
        }
    }
  };

  var chart = new ApexCharts(document.querySelector("#chart9"), options);
  chart.render();



   
// chart 10

var options = {
    series: [{
        name: "Tasks",
        data: [0, 160, 671, 414, 555, 257, 901, 613, 727, 414, 555, 0]
    }],
    chart: {
        type: "area",
        //width: 130,
        height: 55,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 14,
            blur: 4,
            opacity: .12,
            color: "#32bfff"
        },
        sparkline: {
            enabled: !0
        }
    },
    markers: {
        size: 0,
        colors: ["#32bfff"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "35%",
            endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
    stroke: {
        show: !0,
        width: 2.5,
        curve: "smooth"
    },
    fill: {
		type: 'gradient',
		gradient: {
		  shade: 'light',
		  type: 'vertical',
		  shadeIntensity: 0.5,
		  gradientToColors: ['#32bfff'],
		  inverseColors: false,
		  opacityFrom: 0.6,
		  opacityTo: 0.1,
		  //stops: [0, 100]
		}
	  },
    colors: ["#32bfff"],
    xaxis: {
        categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    },
    tooltip: {
        theme: "dark",
        fixed: {
            enabled: !1
        },
        x: {
            show: !1
        },
        y: {
            title: {
                formatter: function(e) {
                    return ""
                }
            }
        },
        marker: {
            show: !1
        }
    }
  };

  var chart = new ApexCharts(document.querySelector("#chart10"), options);
  chart.render();



// chart 11

var options = {
    series: [{
        name: "New Visitors",
        data: [640, 560, 871, 614, 755, 457, 650]
    },{
        name: "Old Visitors",
        data: [440, 360, 671, 414, 555, 257, 450]
    }],
    chart: {
        foreColor: '#9a9797',
        type: "bar",
        //width: 130,
		stacked: true,
        height: 280,
        toolbar: {
            show: !1
        },
        zoom: {
            enabled: !1
        },
        dropShadow: {
            enabled: 0,
            top: 3,
            left: 15,
            blur: 4,
            opacity: .12,
            color: "#3461ff"
        },
        sparkline: {
            enabled: !1
        }
    },
    markers: {
        size: 0,
        colors: ["#3461ff", "#c1cfff"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
            size: 7
        }
    },
    plotOptions: {
        bar: {
            horizontal: !1,
            columnWidth: "35%",
            //endingShape: "rounded"
        }
    },
    dataLabels: {
        enabled: !1
    },
	legend: {
		show: false,
	},
    stroke: {
        show: !0,
        width: 0,
        curve: "smooth"
    },
    colors: ["#3461ff", "#c1cfff"],
    xaxis: {
        categories: ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    },
	grid:{
		show: true,
		borderColor: 'rgba(66, 59, 116, 0.15)',
	},
    tooltip: {
        theme: "dark",
        fixed: {
            enabled: !1
        },
        x: {
            show: !1
        },
        y: {
            title: {
                formatter: function(e) {
                    return ""
                }
            }
        },
        marker: {
            show: !1
        }
    }
  };

  var chart = new ApexCharts(document.querySelector("#chart11"), options);
  chart.render();




// worl map

jQuery('#geographic-map').vectorMap(
	{
		map: 'world_mill_en',
		backgroundColor: 'transparent',
		borderColor: '#818181',
		borderOpacity: 0.25,
		borderWidth: 1,
		zoomOnScroll: false,
		color: '#009efb',
		regionStyle : {
			initial : {
			  fill : '#3461ff'
			}
		  },
		markerStyle: {
		  initial: {
					r: 9,
					'fill': '#fff',
					'fill-opacity':1,
					'stroke': '#000',
					'stroke-width' : 5,
					'stroke-opacity': 0.4
					},
					},
		enableZoom: true,
		hoverColor: '#009efb',
		markers : [{
			latLng : [21.00, 78.00],
			name : 'Lorem Ipsum Dollar'
		  
		  }],
		hoverOpacity: null,
		normalizeFunction: 'linear',
		scaleColors: ['#b6d6ff', '#005ace'],
		selectedColor: '#c9dfaf',
		selectedRegions: [],
		showTooltip: true,
	});





    
});