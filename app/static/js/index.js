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
            renderingType: 'RASTER',
            styles: styles.hide
        });
}

const styles = {
    default: [],
    hide: [
        {
            featureType: 'poi.business',
            stylers: [{ visibility: 'off' }],
        },
        {
            featureType: 'transit',
            elementType: 'labels.icon',
            stylers: [{ visibility: 'off' }],
        },
    ],
};
void init();
// [END maps_advanced_markers_accessibility]
