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

        loadLiveTrains(innerMap, AdvancedMarkerElement, infoWindow);
        setInterval(() => loadLiveTrains(innerMap, AdvancedMarkerElement, infoWindow), 30000);
}

let liveTrainMarkers = [];

async function loadLiveTrains(map, AdvancedMarkerElement, infoWindow) {
    try {
        const response = await fetch('/api/live_trains');

        if (!response.ok) {
            throw new Error('Live trains could not be fetched');
        }

        const trains = await response.json();
        renderLiveTrains(trains, map, AdvancedMarkerElement, infoWindow);
    } catch (error) {
        console.error(error);
    }
}

function renderLiveTrains(trains, map, AdvancedMarkerElement, infoWindow) {
    liveTrainMarkers.forEach(marker => {
        marker.map = null;
    });
    liveTrainMarkers = [];

    trains
        .filter(train => trainLocation(train))
        .forEach((train, index) => {
            const marker = new AdvancedMarkerElement({
                map,
                position: liveTrainPosition(train, index),
                title: liveTrainTitle(train),
                content: liveTrainDot(train.route_id),
            });

            marker.addListener('click', () => {
                infoWindow.close();
                infoWindow.setContent(buildTrainInfoContent(train));
                infoWindow.open(map, marker);
            });

            liveTrainMarkers.push(marker);
        });
}

function liveTrainPosition(train, index) {
    const location = trainLocation(train);
    const angle = index * 2.399963229728653;
    const offset = 0.00012 * ((index % 4) + 1);

    return {
        lat: location.lat + Math.sin(angle) * offset,
        lng: location.lng + Math.cos(angle) * offset,
    };
}

function trainLocation(train) {
    if (train.lat && train.lng) {
        return { lat: train.lat, lng: train.lng };
    }

    if (train.next_stop?.lat && train.next_stop?.lng) {
        return { lat: train.next_stop.lat, lng: train.next_stop.lng };
    }

    return null;
}

function liveTrainDot(route) {
    if (route.toUpperCase() === 'FS') route = 'SF';
    if (route.toUpperCase() === 'H') route = 'SR';
    if (route.toUpperCase() === 'SI') route = 'SIR';
    const routeKey = routeIconName(route);
    const color = LINE_COLORS[routeKey?.toUpperCase()] ?? '#111';
    const dot = document.createElement('div');
    dot.className = 'live-train-dot';
    dot.style.background = color;
    dot.textContent = route || '?';
    return dot;
}

function liveTrainTitle(train) {
    const station = train.current_station_name || train.next_stop?.station_name || 'unknown station';
    return `${train.route_id || ''} train near ${station}`.trim();
}

function buildTrainInfoContent(train) {
    let route = routeIconName(train.route_id)?.toLowerCase();
    const icon = route ? `<img src="/static/svg/${route}.svg" width="28" height="28" alt="${train.route_id}" title="${train.route_id}">` : '';
    const station = train.current_station_name || train.next_stop?.station_name || 'Unknown station';
    const status = train.current_status?.replaceAll('_', ' ').toLowerCase() || 'status unknown';
    const nextStop = train.next_stop?.station_name ? `<div style="font-size:12px;margin-top:4px">Next: ${train.next_stop.station_name}</div>` : '';
    if (train.route_id === 'FS') train.route_id = 'Franklin Shuttle';
    if (train.route_id === 'H') train.route_id = 'Rockaway Shuttle';
    if (train.route_id === 'SI') train.route_id = 'SIR';
    return `<div style="font-family:sans-serif;padding:4px 2px">
        <div style="display:flex;gap:6px;align-items:center;margin-bottom:6px">
            ${icon}
            <div style="font-weight:600;font-size:14px">${train.route_id || 'Train'} train</div>
        </div>
        <div style="font-size:13px">${station}</div>
        <div style="font-size:12px;color:#555;margin-top:4px">${status}</div>
        ${nextStop}
    </div>`;
}

function routeIconName(route) {
    if (!route) {
        return null;
    }
    if (route.toUpperCase() === 'FS') return 'SF';
    if (route.toUpperCase() === 'H') return 'SR';
    return route.toUpperCase() === 'SI' ? 'SIR' : route;
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
    let routeCount = routes.split(' ').length
    if (routeCount <= 2) routeCount = 0;
    const color = LINE_COLORS[firstRoute] ?? '#555';
    const dot = document.createElement('div');
    dot.style.cssText = [
        `width:${10+routeCount}px`, `height:${10+routeCount}px`, 'border-radius:50%',
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
