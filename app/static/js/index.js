'use strict';
/**
 * @license
 * Copyright 2019 Google LLC. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

// [START maps_advanced_markers_accessibility]

async function init() {
    // Request needed libraries.
    const [{ InfoWindow }, { AdvancedMarkerElement, PinElement }] =
        await Promise.all([
            google.maps.importLibrary('maps'),
            google.maps.importLibrary('marker'),
        ]);
        const mapElement = document.querySelector('gmp-map');
        const innerMap = mapElement.innerMap;

        innerMap.setOptions({
            // Disable the default UI.
            disableDefaultUI: true,
            styles: styles.hide
        });
        const transitLayer = new google.maps.TransitLayer();
        transitLayer.setMap(innerMap);

        const infoWindow = new InfoWindow();

        for (const station of STATIONS) {
            const marker = new AdvancedMarkerElement({
                map: innerMap,
                position: { lat: station['GTFS Latitude'], lng: station['GTFS Longitude'] },
                title: station['Stop Name'],
                content: stationDot(station['Daytime Routes']),
            });

            marker.addListener('click', () => {
                infoWindow.close();
                infoWindow.setContent(buildInfoContent(station));
                infoWindow.open(innerMap, marker);
            });
        }
}

const LINE_COLORS = {
    '1': '#EE352E', '2': '#EE352E', '3': '#EE352E',
    '4': '#00933C', '5': '#00933C', '6': '#00933C', '6D': '#00933C',
    '7': '#B933AD', '7D': '#B933AD',
    'A': '#0039A6', 'C': '#0039A6', 'E': '#0039A6',
    'B': '#FF6319', 'D': '#FF6319', 'F': '#FF6319', 'FD': '#FF6319', 'M': '#FF6319',
    'G': '#6CBE45',
    'J': '#996633', 'Z': '#996633',
    'L': '#A7A9AC',
    'N': '#FCCC0A', 'Q': '#FCCC0A', 'R': '#FCCC0A', 'W': '#FCCC0A',
    'S': '#808183', 'SF': '#808183', 'SR': '#808183',
    'H': '#0039A6',
    'SIR': '#0039A6',
    'T': '#00A1DE',
};

function stationDot(routes) {
    const firstRoute = routes.split(' ')[0].toUpperCase();
    const color = LINE_COLORS[firstRoute] ?? '#555';
    const dot = document.createElement('div');
    dot.style.cssText = [
        'width:10px', 'height:10px', 'border-radius:50%',
        `background:${color}`, 'border:1.5px solid white',
        'box-shadow:0 1px 3px rgba(0,0,0,0.35)', 'cursor:pointer',
    ].join(';');
    return dot;
}

function buildInfoContent(station) {
    const icons = station['Daytime Routes']
        .split(' ')
        .map(r => `<img src="/static/svg/${r.toLowerCase()}.svg" width="28" height="28" alt="${r}" title="${r}">`)
        .join('');
    return `<div style="font-family:sans-serif;padding:4px 2px">
        <div style="font-weight:600;font-size:14px;margin-bottom:6px">${station['Stop Name']}</div>
        <div style="display:flex;gap:4px;align-items:center">${icons}</div>
    </div>`;
}

const styles = {
    default: [],
    hide: [
        {
            featureType: 'transit.station',
            stylers: [{ visibility: 'off' }],
        },
        {
            featureType: 'poi',
            elementType: 'labels.icon',
            stylers: [{ visibility: 'off' }],
        },
    ],
};
void init();
// [END maps_advanced_markers_accessibility]
