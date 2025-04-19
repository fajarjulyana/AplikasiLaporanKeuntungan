/**
 * Creates a line chart with the provided data
 * @param {string} chartId - The ID of the canvas element
 * @param {Array} labels - The labels for the x-axis
 * @param {Array} data - The data points for the chart
 * @param {string} label - The label for the dataset
 * @param {boolean} fill - Whether to fill the area under the line
 */
function createLineChart(chartId, labels, data, label = 'Data', fill = false) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: 'rgba(78, 115, 223, 1)',
                pointHoverRadius: 5,
                pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: fill
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                },
                y: {
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        // Include a rupiah sign in the ticks
                        callback: function(value, index, values) {
                            return 'Rp ' + value.toLocaleString('id-ID');
                        }
                    },
                    grid: {
                        color: "rgba(128, 128, 128, 0.1)",
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    backgroundColor: "rgb(30, 30, 30)",
                    bodyFont: {
                        size: 14
                    },
                    titleMarginBottom: 10,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(220, 220, 220, 0.1)',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    intersect: false,
                    mode: 'index',
                    caretPadding: 10,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return label + ': Rp ' + value.toLocaleString('id-ID');
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a pie chart with the provided data
 * @param {string} chartId - The ID of the canvas element
 * @param {Array} labels - The labels for the chart
 * @param {Array} data - The data points for the chart
 */
function createPieChart(chartId, labels, data) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    // Generate color palette based on number of categories
    const colors = generateColorPalette(labels.length);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round(value / total * 100);
                            return label + ': Rp ' + value.toLocaleString('id-ID') + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a doughnut chart with the provided data
 * @param {string} chartId - The ID of the canvas element
 * @param {Array} labels - The labels for the chart
 * @param {Array} data - The data points for the chart
 */
function createDoughnutChart(chartId, labels, data) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    // Generate color palette based on number of categories
    const colors = generateColorPalette(labels.length);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round(value / total * 100);
                            return label + ': Rp ' + value.toLocaleString('id-ID') + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a bar chart with the provided data
 * @param {string} chartId - The ID of the canvas element
 * @param {Array} labels - The labels for the x-axis
 * @param {Array} datasets - The datasets for the chart
 */
function createBarChart(chartId, labels, datasets) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                },
                y: {
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        // Include a rupiah sign in the ticks
                        callback: function(value, index, values) {
                            return 'Rp ' + value.toLocaleString('id-ID');
                        }
                    },
                    grid: {
                        color: "rgba(128, 128, 128, 0.1)",
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    backgroundColor: "rgb(30, 30, 30)",
                    bodyFont: {
                        size: 14
                    },
                    titleMarginBottom: 10,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(220, 220, 220, 0.1)',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    intersect: false,
                    mode: 'index',
                    caretPadding: 10,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return label + ': Rp ' + value.toLocaleString('id-ID');
                        }
                    }
                }
            }
        }
    });
}

/**
 * Generates a color palette with the specified number of colors
 * @param {number} count - The number of colors to generate
 * @returns {Array} An array of colors
 */
function generateColorPalette(count) {
    const baseColors = [
        'rgba(78, 115, 223, 0.8)',
        'rgba(28, 200, 138, 0.8)',
        'rgba(54, 185, 204, 0.8)',
        'rgba(246, 194, 62, 0.8)',
        'rgba(231, 74, 59, 0.8)',
        'rgba(90, 92, 105, 0.8)',
        'rgba(133, 135, 150, 0.8)',
        'rgba(0, 123, 255, 0.8)',
        'rgba(40, 167, 69, 0.8)',
        'rgba(255, 193, 7, 0.8)'
    ];
    
    // If we need more colors than in our base set, we'll generate them
    if (count <= baseColors.length) {
        return baseColors.slice(0, count);
    }
    
    // Generate additional colors by adjusting hue
    const colors = [...baseColors];
    const hueStep = 360 / (count - baseColors.length);
    
    for (let i = baseColors.length; i < count; i++) {
        const hue = Math.floor((i - baseColors.length) * hueStep);
        colors.push(`hsla(${hue}, 70%, 60%, 0.8)`);
    }
    
    return colors;
}
