
// Make an AJAX request to the API endpoint to get the customer locations
var xhr = new XMLHttpRequest();
xhr.open('GET', '/get_customers', true);
xhr.onload = function() {
  // Parse the JSON response and extract the customer locations
  var customers = JSON.parse(xhr.responseText);
  
  // Initialize and display the map
  initMap(customers);
};
xhr.send();

// Initialize and display the map using the customer locations
function initMap(customers) {
  // Set the coordinates of the customer location
  var customerLoc = { lat: 13.7563, lng: 100.5018 };
  
  // Create a new map centered at the customer location
  var map = new google.maps.Map(document.getElementById("map"), {
    center: customerLoc,
    zoom: 10,
  });
  
  // Loop through the customers array and add a marker for each customer
  for (let i = 0; i < customers.length; i++) {
    const customer = customers[i];
    const latLng = new google.maps.LatLng(customer.lat, customer.lng);
    const marker = new google.maps.Marker({
      position: latLng,
      map: map,
    });
    
    // Add a click event listener to the marker
    marker.addListener("click", function () {
      // Show the customer name in an info window
      const infowindow = new google.maps.InfoWindow({
        content: `<h3>${customer.name}</h3>`,
      });
      infowindow.open(map, marker);
    });
  }
}
