'use strict';
/**
 * @license
 * Copyright 2019 Google LLC. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

// [START maps_advanced_markers_accessibility]
const mapElement = document.querySelector('gmp-map');


async function init() {
    // Request needed libraries.
    const [{ InfoWindow }, { AdvancedMarkerElement, PinElement }] =
        await Promise.all([
            google.maps.importLibrary('maps'),
            google.maps.importLibrary('marker'),
        ]);

    // Create an info window to share between markers.
    const infoWindow = new InfoWindow();

    // Create the markers.
    tourStops.forEach(({ position, title }, i) => {
        // [START maps_advanced_markers_accessibility_marker]
        const pin = new PinElement({
            glyphText: `${i + 1}`,
            scale: 1.5,
        });
        const marker = new AdvancedMarkerElement({
            position,
            title: `${i + 1}. ${title}`,
            gmpClickable: true,
        });
        marker.append(pin);
        mapElement.append(marker);

        // [END maps_advanced_markers_accessibility_marker]
        // [START maps_advanced_markers_accessibility_event_listener]
        // Add a click listener for each marker, and set up the info window.
        marker.addEventListener('gmp-click', () => {
            infoWindow.close();
            infoWindow.setContent(marker.title);
            infoWindow.open(marker.map, marker);
        });
        // [END maps_advanced_markers_accessibility_event_listener]
    });
}

void init();
// [END maps_advanced_markers_accessibility]
