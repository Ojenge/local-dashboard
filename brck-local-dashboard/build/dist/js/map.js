// Map JS functions for Monitoring tool

// set markers
function setMarkers(vLat,vLong) {
  // marker
  var mojaMarker = new google.maps.Marker({
    position: {lat: vLat, lng: vLong},
    title: "Moja Location",
    icon: '../../dist/img/location-marker.png'
  });

  mojaMarker.setMap(mojaMap);
}


// get map coordinates in JSON format
function getCoordinates() {
  jQuery.ajax({
    url: 'https://operations.brck.io/device/api/v1.0/gps',
    type: 'GET',
    dataType: 'json',
    success: function(response) {
      for (var i = 0; i < response.length; i++) {
        var obj = response[i];
//         debug via web browser console; enable when needed
         console.log(response[i]);
         console.log(obj.latitude);
         console.log(obj.longitude);
//         pass coordinates to setMarkers
        setMarkers(parseFloat(obj.latitude), parseFloat(obj.longitude));
      }
    },
    error: function(error) {
      console.log(error);
    }
  });
}


// Moja Locations using Google Maps
var map;

// position
var mojaPosition = {lat: -1.298928, lng: 36.793205};

function initMap() {
  mojaMap = new google.maps.Map(document.getElementById('map'), {
    center: {lat: -1.298928, lng: 36.793205},
    zoom: 14,
    styles: [
            {elementType: 'geometry', stylers: [{color: '#eeeeee'}]},
            {
              elementType: 'labels.text.fill',
              stylers: [{color: '#777777'}]
            },
            {
              elementType: 'labels.text.stroke',
              stylers: [{color: '#ffffff'}]
            },
            {
              featureType: 'poi',
              elementType: 'geometry',
              stylers: [{color: '#f5f5f5'}]
            },
            {
              featureType: 'poi',
              elementType: 'labels.text.fill',
              stylers: [{color: '#777777'}]
            },
            {
              featureType: 'road',
              elementType: 'geometry',
              stylers: [{color: '#cccccc'}]
            },
            {
              featureType: 'road',
              elementType: 'geometry.stroke',
              stylers: [{color: '#ffffff'}]
            },
            {
              featureType: 'road.highway',
              elementType: 'geometry.fill',
              stylers: [{'color': '#ffffff'}]
            },
            {
              featureType: 'road.arterial',
              elementType: 'geometry',
              stylers: [{'color': '#ffffff'}]
            },

            {
              featureType: 'road.local',
              elementType: 'geometry',
              stylers: [{'color': '#ffffff'}]
            },
            {
              featureType: 'transit.station',
              elementType: 'labels.text.fill',
              stylers: [{color: '#999999'}]
            },
            {
              elementType: 'labels.icon',
              stylers: [{'visibility': 'off'}]
            },
          ]
  });

  // set markers
  getCoordinates();
}
