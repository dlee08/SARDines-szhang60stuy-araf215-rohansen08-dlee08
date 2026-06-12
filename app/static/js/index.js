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
      /*  const center = new google.maps.LatLng({ lat: 40.728474975408446, lng: -73.96241785378106 });
        const zoom = 4;
        google.maps.Map(document.getElementById("gmp-map"), {
          zoom,
          center,
          minZoom: zoom - 3,
          maxZoom: zoom + 3,
          restriction: {
            latLngBounds: {
              north: -10,
              south: -40,
              east: 160,
              west: 100,
            },
          },
      }); */

        const mapElement = document.querySelector('gmp-map');
        const innerMap = mapElement.innerMap;

        innerMap.setOptions({
            // Disable the default UI.
            disableDefaultUI: true,
            clickableIcons: false,
            styles: styles.hide,
        });
        const transitLayer = new google.maps.TransitLayer();
        transitLayer.setMap(innerMap);

        const infoWindow = new InfoWindow({
            headerDisabled: true,
        });
        innerMap.addListener('click', () => {
            infoWindow.close();
        });
        const elevatorResponse = await fetch('/api/elevator');
        const elevatorOutage = await elevatorResponse.json();

        const stopTimes = await fetch('/api/stop_times');
        const timeJson = await stopTimes.json();

        for (const station of STATIONS) {
            const marker = new AdvancedMarkerElement({
                map: innerMap,
                position: { lat: station['GTFS Latitude'], lng: station['GTFS Longitude'] },
                title: station['Stop Name'],
                content: stationDot(station['Daytime Routes']),
            });

            marker.addListener('click', () => {
                console.log('Station:', station);
                console.log('Stop times:', timeJson[station['Complex ID']]);
                infoWindow.close();
                infoWindow.setContent(buildInfoContent(station, elevatorOutage, timeJson));
                infoWindow.open(innerMap, marker);
            });
        }

        for (const station of RAILROAD_STATIONS) {
            const marker = new AdvancedMarkerElement({
                map: innerMap,
                position: {
                    lat: Number(station['Latitude']),
                    lng: Number(station['Longitude'])
                },
                title: station['Station Name'],
                content: railroadStationDot(station['Railroad']),
            });

            marker.addListener('click', () => {
                infoWindow.close();
                infoWindow.setContent(buildRailroadInfoContent(station));
                infoWindow.open(innerMap, marker);
            });
}
        loadLiveTrains(innerMap, AdvancedMarkerElement, infoWindow);
        loadLiveLIRR(innerMap, AdvancedMarkerElement, infoWindow);
        setInterval(async () => {
            await Promise.all([
                loadLiveTrains(innerMap, AdvancedMarkerElement, infoWindow),
                loadLiveLIRR(innerMap, AdvancedMarkerElement, infoWindow)
            ]);
            sweepTrains();
        }, 30000);
        //setInterval(() => loadLiveTrains(innerMap, AdvancedMarkerElement, infoWindow), 30000);
        //setInterval(() => loadLiveLIRR(innerMap, AdvancedMarkerElement, infoWindow), 30000);
}

let liveTrainMarkers = {};

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

async function loadLiveLIRR(map, AdvancedMarkerElement, infoWindow) {
    try {
        const response = await fetch('/api/live_lirr');
        if (!response.ok) {
            throw new Error('Live lirr could not be fetched');
        }

        const trains_lirr = await response.json();
        renderLiveLIRR(trains_lirr, map, AdvancedMarkerElement, infoWindow);
    } catch (error) {
        console.error(error);
    }
}

function renderLiveTrains(trains, map, AdvancedMarkerElement, infoWindow) {
    trains
        .filter(train => trainLocation(train))
        //.filter(train => train.current_station_name !== train.next_stop?.station_name)
        .forEach((train, index) => {
            const id = train.trip_id;
            const newPos = liveTrainPosition(train, index);
            const existing = liveTrainMarkers[id];

            if (existing) {
                animateMarkerTo(existing.marker, newPos);
                existing.marker.title = liveTrainTitle(train);
                existing.train = train;
                existing.seen = true;
            } else {
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

                liveTrainMarkers[id] = {marker, train, seen: true};
            }
        });
}

function renderLiveLIRR(trains, map, AdvancedMarkerElement, infoWindow) {

    trains
        .filter(train => trainLocation(train))
        //.filter(train => train.current_station_name !== train.next_stop?.station_name)
        .forEach((train, index) => {
            const id = train.trip_id;
            const newPos = liveTrainPosition(train, index);
            const existing = liveTrainMarkers[id];

            if (existing) {
                animateMarkerTo(existing.marker, newPos);
                existing.marker.title = liveTrainTitle(train);
                existing.train = train;
                existing.seen = true;
            }
            else {
                const marker = new AdvancedMarkerElement({
                    map,
                    position: liveTrainPosition(train, index),
                    title: liveTrainTitle(train),
                    content: liveTrainDot(train.railroad),
                });

                marker.addListener('click', () => {
                    infoWindow.close();
                    infoWindow.setContent(buildTrainInfoContent(train));
                    infoWindow.open(map, marker);
                });

                liveTrainMarkers[id] = {marker, train, seen: true};
            }
        });
}

// remove markers for trains that disappeared
function sweepTrains() {
    for (const id in liveTrainMarkers) {
        if (!liveTrainMarkers[id].seen) {
            liveTrainMarkers[id].marker.map = null;
            delete liveTrainMarkers[id];
        }
        else {
            liveTrainMarkers[id].seen = false;
        }
    }
}

function animateMarkerTo(marker, newPos, duration = 1000) {
    const startPos = {
        lat: marker.position.lat,
        lng: marker.position.lng,
    };

    const dist = Math.abs(newPos.lat - startPos.lat) + Math.abs(newPos.lng - startPos.lng);
    if (dist < 0.000001) return;

    const startTime = performance.now();

    function step(now) {
        let t = (now - startTime) / duration;
        if (t > 1) t = 1;

        const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;

        marker.position = {
            lat: startPos.lat + (newPos.lat - startPos.lat) * eased,
            lng: startPos.lng + (newPos.lng - startPos.lng) * eased,
        };

        if (t < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
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
    if (route.toUpperCase() === 'GS') route = 'S';
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
    if (train.route_id === 'GS') train.route_id = 'S';
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
    if (route.toUpperCase() === 'GS') return 'S';
    if (route.toUpperCase() === 'FS') return 'SF';
    if (route.toUpperCase() === 'H') return 'SR';
    return route.toUpperCase() === 'SI' ? 'SIR' : route;
}

const LINE_COLORS = {
    '1': '#EE352E', '2': '#EE352E', '3': '#EE352E',
    '4': '#00933C', '5': '#00933C', '6': '#00933C', '6X': '#00933C',
    '7': '#B933AD', '7X': '#B933AD',
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
    'LI': '#0039A6',
    'MN': '#EE352E',
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

function railroadStationDot(railroad) {
    const dot = document.createElement('div');

    const color = railroad === 'LIRR'
        ? '#0044ff'
        : '#37ff00';

    dot.style.cssText = [
        'width:12px',
        'height:12px',
        'border-radius:50%',
        `background:${color}`,
        'border:1.5px solid white',
        'box-shadow:0 1px 3px rgba(0,0,0,0.35)',
        'cursor:pointer',
    ].join(';');

    return dot;
}

function buildRailroadInfoContent(station) {
    const railroadName = station['Railroad'] === 'LIRR'
        ? 'Long Island Rail Road'
        : 'Metro-North Railroad';

    return `
        <div style="font-family:sans-serif;padding:4px 2px;max-width:260px">
            <div style="font-weight:600;font-size:14px;margin-bottom:6px">
                ${station['Station Name']}
            </div>

            <div style="font-size:13px">
                <div><b>Railroad:</b> ${railroadName}</div>
                <div><b>Branch:</b> ${station['Branch']}</div>
                <div><b>Zone:</b> ${station['Zone']}</div>
                <div><b>Accessibility:</b> ${station['Accessibility']}</div>
                <div style="margin-top:6px"><b>Outbound:</b> ${station['Outbound Title']}</div>
                <div><b>Inbound:</b> ${station['Inbound Title']}</div>
            </div>

            <div style="margin-top:8px">
                <a href="${station['Station URL']}" target="_blank">Station info</a>
            </div>
        </div>
    `;
}

function buildInfoContent(station, elevatorOutage, timeJSON) {
    const outage = elevatorOutage.filter(o =>
    o.station.toLowerCase() === station['Stop Name'].toLowerCase()
    );
    const trains = timeJSON[station['Complex ID']] || [];
    trains.sort(function (a, b) {
      return a.time_to_arrive.localeCompare(b.time_to_arrive, undefined, {'numeric': true});
    });

    // Group trains by route + destination
    const grouped = {};
    for (const t of trains) {
        const key = `${t.route}|${t.destination || t.direction}`;
        if (!grouped[key]) {
            grouped[key] = { route: t.route, destination: t.destination || t.direction, times: [] };
        }
        grouped[key].times.push(t.time_to_arrive);
    }

    const trainsHtml = Object.keys(grouped).length ? Object.values(grouped).map(g =>
        `<div>${g.route} → ${g.destination}: ${g.times.join(', ')} min</div>`
    ).join('') : '<div style="color:#555">No upcoming trains</div>';
    const outageHtml = outage.length ? outage.map(outage => `
    <hr style="margin:8px 0">
    <div style="font-size:13px; max-width: 250px">
        <div><b>Type:</b> ${outage.type === 'EL' ? 'Elevator' : 'Escalator'}</div>
        <div><b>Reason:</b> ${outage.reason}</div>
        <div><b>Outage started:</b> ${outage.outage_date}</div>
        <div><b>Estimated return:</b> ${outage.est_return}</div>
        <div style="margin-top:5px"><b>Affected path:</b> ${outage.serving_info}</div>
    </div>
    `).join('') : `
        <div style="font-size:13px;color:#555"></div>
    `;
    const icons = station['Daytime Routes']
        .split(' ')
        .map(r => `<img src="/static/svg/${r.toLowerCase()}.svg" width="28" height="28" alt="${r}" title="${r}">`)
        .join('');
    return `<div style="font-family:sans-serif;padding:4px 2px">
        <div style="font-weight:600;font-size:14px;margin-bottom:6px">${station['Stop Name']}</div>
        <div style="display:flex;gap:4px;align-items:center">${icons}</div>
        <div style="margin-top:8px;font-size:12px">${trainsHtml}</div>
        ${outageHtml}
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
