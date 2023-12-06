__all__ = ['ALERT_TRIGGER', 'INTERACTION_TRIGGER']

ALERT_TRIGGER = "window.alert_trigger = false;window.alert = function() {window.alert_trigger = true;};window.confirm = window.alert;window.prompt = window.alert;"
INTERACTION_TRIGGER = """
var ids = {0};
for (var i = 0; i < ids.length; i++) {{
    var element = document.getElementById(ids[i]);
    if(!element) continue;
    var events = ['click', 'mouseover', 'mousedown', 'mouseup', 'mousemove', 'mouseout', 'mouseenter', 'mouseleave', 'dblclick', 'contextmenu', 'wheel', 'select', 'pointerdown', 'pointerup', 'pointermove', 'pointerover', 'pointerout', 'pointerenter', 'pointerleave', 'gotpointercapture', 'lostpointercapture'];
    try {{
        for (var j = 0; j < events.length; j++) {{
            var event = new MouseEvent(events[j], {{bubbles: true}});
            element.dispatchEvent(event);
        }}
        element.focus();
        element.blur();
        element.dispatchEvent(new KeyboardEvent('keydown', {{ctrlKey: true, altKey: true, key: 'x'}}));
    }} catch (e) {{}}
}}
                """
