import asyncio
import subprocess
from functools import partial

from percy import percySnapshot
from selenium.webdriver import Chrome

import pywebio
import template
import util
from pywebio import start_server
from pywebio.output import *
from pywebio.session import *
from pywebio.utils import *


def target():
    set_auto_scroll_bottom(False)

    # test session data
    g = data()
    assert g.none is None
    g.one = 1
    g.one += 1
    assert g.one == 2

    # test pywebio.utils
    async def corofunc(**kwargs):
        pass

    def genfunc(**kwargs):
        yield

    corofunc = partial(corofunc, a=1)
    genfunc = partial(genfunc, a=1)

    assert isgeneratorfunction(genfunc)
    assert iscoroutinefunction(corofunc)
    assert get_function_name(corofunc) == 'corofunc'

    get_free_port()

    # test pywebio.output
    set_output_fixed_height(False)

    try:
        yield put_buttons([{'label': 'must not be shown'}], onclick=[lambda: None])
    except Exception:
        pass

    put_table([
        ['Idx', 'Actions'],
        ['1', table_cell_buttons(['edit', 'delete'], onclick=lambda _: None)],
    ])

    popup('title', 'html content')
    popup('title2', 'html content')
    close_popup()

    with use_scope() as name:
        put_text('no show')
    remove(name)

    with use_scope('test') as name:
        put_text('current scope name:%s' % name)

    with use_scope('test', clear=True):
        put_text('clear previous scope content')

    @use_scope('test')
    def scoped_func(text):
        put_text(text)

    scoped_func('text1 from `scoped_func`')
    scoped_func('text2 from `scoped_func`')

    try:
        put_column([put_text('A'), 'error'])
    except Exception:
        pass

    yield hold()


async def corobased():
    await wait_host_port(port=8080, host='127.0.0.1')
    await to_coroutine(target())


def threadbased():
    run_as_function(target())


def test(server_proc: subprocess.Popen, browser: Chrome):
    time.sleep(2)
    percySnapshot(browser=browser, name='misc output')

    coro_out = template.save_output(browser)[-1]

    browser.get('http://localhost:8080/?app=thread')
    time.sleep(2)

    thread_out = template.save_output(browser)[-1]

    assert coro_out == thread_out


def start_test_server():
    pywebio.enable_debug()
    start_server({'coro': corobased, 'thread': threadbased}, port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    util.run_test(start_test_server, test, address='http://localhost:8080/?app=coro')
