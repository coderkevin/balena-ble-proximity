const express = require( 'express' );
const app = express(); 

// Enable HTML template middleware
app.engine( 'html', require('ejs').renderFile );

// Enable static CSS styles
app.use( express.static( 'styles' ) );

// Show index page
app.get( '/', function( req, res ) {
	res.render( 'index.html' );
} );

// Start server on port 90, log its start to console
const server = app.listen( 80, function() {
	const port = server.address().port;
	console.log('ble-proximity listening on port ', port);
} );
