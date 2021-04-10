# Copyright (c) 2008, Aldo Cortesi. All rights reserved.
# Copyright (c) 2017, Dirk Hartmann.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile.layout.base import _SimpleLayoutBase
from libqtile import drawer, hook, window; #YOBLECK
#myd = drawer.Drawer(); #yobleck

def log_test(i):
    f = open("/home/yobleck/qtile_log.txt","a");
    f.write(str(i));
    f.close();

class BrowserTab2(_SimpleLayoutBase):
    """Maximized layout

    A simple layout that only displays one window at a time, filling the
    screen_rect. This is suitable for use on laptops and other devices with
    small screens. Conceptually, the windows are managed as a stack, with
    commands to switch to next and previous windows in the stack.
    """

    defaults = [("name", "browsertab2", "Name of this layout.")]

    def __init__(self, **config):
        _SimpleLayoutBase.__init__(self, **config)
        self.add_defaults(BrowserTab2.defaults)
        
        self.panel_width = 1000;
        self._panel = None;
        self._drawer = None;
        self._layout = None;
    
    def show(self, screen_rect): #TODO: drawer.draw() then place then finalize?
        log_test("showing\n");
        self._create_panel(screen_rect);
        #self._panel.place(screen_rect.x, screen_rect.y, screen_rect.width, screen_rect.height-980, 0, None);
        self._create_drawer(screen_rect);
        self.draw_panel();
        self._panel.unhide();
    
    def _create_panel(self, screen_rect):
        log_test("creating panel\n");
        self._panel = window.Internal.create(self.group.qtile, screen_rect.x, screen_rect.y, screen_rect.width, 100);
        log_test("panel: " + str(self._panel) + "\n");
        self._panel.place(screen_rect.x, screen_rect.y, screen_rect.width, screen_rect.height-956, 0, None);
        #self._create_drawer(screen_rect);
        self.group.qtile.windows_map[self._panel.window.wid] = self._panel;
        hook.subscribe.client_name_updated(self.draw_panel);
        hook.subscribe.focus_change(self.draw_panel);
        log_test("created panel\n");
    
    def _create_drawer(self, screen_rect):
        log_test("creating drawer\n");
        log_test("screen_rect: " + str(screen_rect) + "\n");
        self._drawer = drawer.Drawer(self.group.qtile, self._panel.window.wid, screen_rect.width, 100); #screen_rect.height
        log_test("drawer: " + str(self._drawer) + "\n");
        self._drawer.clear("#0000ff");
        #self._layout = 
        self._drawer.textlayout("test text", "#ff0000", "sans", 20, None);
        log_test("created drawer\n");
        
    def draw_panel(self, *args):
        log_test("drawing\n");
        self._drawer.clear("#00ff00");
        self._drawer.textlayout("test text", "#ff0000", "sans", 20, None);
        self._drawer.draw(offsetx=0, width=self.panel_width);
        log_test("drawededed\n");
        
    
    def clone(self, group):
        return _SimpleLayoutBase.clone(self, group)

    def add(self, client):
        log_test("adding client: " + str(client) + " to list: " +str(self.clients) + "\n");
        return self.clients.add(client, 1)

    def configure(self, client, screen_rect):
        
        if self.clients and client is self.clients.current_client:
            client.place(
                screen_rect.x,
                screen_rect.y+100,
                screen_rect.width,
                screen_rect.height-100,
                0,
                None
            )
            client.unhide()
            #log_test("self.group and self.group.qtile: " + str(self.group) + " " + str(self.group.qtile) + "\n"); #YOBLECK
            log_test("configuring client: " + str(client) + " with screen rect: " + str(screen_rect) + "\n");
        else:
            client.hide()
        self.show(screen_rect);

    cmd_previous = _SimpleLayoutBase.previous
    """def cmd_previous(self, screen_rect):
        _SimpleLayoutBase.previous;
        self._create_panel(screen_rect);
        self._panel.place(screen_rect.x, screen_rect.y,screen_rect.width, screen_rect.height,0,None);
        self._create_drawer(screen_rect);
        self.draw_panel();
    cmd_previous = self.cmd_previous(screen_rect);"""
    cmd_next = _SimpleLayoutBase.next

    cmd_up = cmd_previous
    cmd_down = cmd_next
