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

import json
import time

from libqtile import qtile
from libqtile.popup import Popup
from libqtile.widget import GenPollUrl
from xcffib.xproto import StackMode


def log(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class FaH(GenPollUrl):
    """
    Folding @ Home user's statistics widget
    with optional popup background window
    """

    defaults = [
        (
            "username",
            "anonymous",
            "Username or user id to poll."
        ),
        (   "is_popup",
            False,
            "Display text with popup window? Defaults to bar"
        ),
        (
            "popup_struct",
            (10,10,200,100,"#000000",1),
            "Location and size of the F@H popup window. (x, y, width, height, border_color, border_width)"
        )
    ]

    def __init__(self, **config):
        GenPollUrl.__init__(self, **config)
        self.add_defaults(FaH.defaults)
        self.BASE_URL = "https://api.foldingathome.org/user/"
        self.url = self.BASE_URL + self.username
        self.popup = None
        self.updater_pid = -1

    # def _configure(self):
        #bases._TextBox._configure(self)
        #move popup creation into here

    def poll(self):
        try:
            with open("/home/yobleck/.config/qtile/fah_widget/fah_stats.txt", "r") as f:
                body = json.load(f)
            #body = {"name":"yobleck","id":725476,"score":46455889,"wus":7483,"rank":45348,"active_50":2,"active_7":1,"last":"2022-09-03 17:42:28","users":2934121,"teams":[{"team":223518,"name":"LinusTechTips_Team","score":46455389,"wus":7479,"last":"2022-09-03 17:42:28","active_50":0,"active_7":0},{"team":225605,"name":"PC Master Race - PCMR","score":500,"wus":4,"active_50":0,"active_7":0}],"projects":[9019,9020]}
            #log(body)
        except Exception as e:#URLError:
            log(e)
            return "No network"

        if not self.is_popup:  # update bar text only version
            text = f"{body['name']}: Score:{body['score']}, WUs:{body['wus']}, Rank:{body['rank']}"
            return text

        elif not self.popup:  # create initial popup window. this should only run once. TODO self.configure method
            try:
                self.updater_pid = qtile.cmd_spawn(f"python /home/yobleck/.config/qtile/fah_widget/fah_update.py {self.update_interval}")

                self.popup = Popup(qtile, background="#00000000", foreground=self.foreground,
                                    x=self.popup_struct[0], y=self.popup_struct[1], width=self.popup_struct[2], height=self.popup_struct[3],
                                    font=self.font, font_size=self.fontsize, border=self.popup_struct[4], border_width=self.popup_struct[5],
                                    opacity=1, wrap=True)

                # place window. stackmode below is required to ensure the windows stay below all other windows
                # replaces the default self.popup.place() function
                self.popup.win.window.set_property("_NET_WM_STATE", (343,))  # "_NET_WM_STATE_BELOW" = (343,)
                self.popup.win.window.configure(x=self.popup.x, y=self.popup.y,
                                                width=self.popup.width, height=self.popup.height, stackmode=StackMode.Below)
                self.popup.win.paint_borders(self.popup.border, self.popup.border_width)
                self.popup.unhide()

                # draw text
                self.popup.text = f"{body['name']}\nScore: {body['score']:,}\nWUs: {body['wus']:,}\nRank: {body['rank']:,}/{body['users']:,}\nTop: {100*int(body['rank'])/int(body['users']):.2f}%"
                #self.clear()
                self.popup.draw_text(x=4, y=2)
                self.popup.draw()

                self.popup.win.process_button_click = self.noop
            except Exception as e:
                log(e)
            return ""  # f"created {time.asctime()}"

        elif self.is_popup and self.popup:  # update popup window. BUG redraw cause current window to lose focus/intercept mouse inputs?
            try:
                self.popup.clear()
                self.popup.text = f"{body['name']}\nScore: {body['score']:,}\nWUs: {body['wus']:,}\nRank: {body['rank']:,}/{body['users']:,}\nTop: {100*int(body['rank'])/int(body['users']):.2f}%"
                self.popup.draw_text(x=4, y=2)
                self.popup.draw()
            except Exception as e:
                log(e)
            return ""  # f"updated {time.asctime()}"
        else:
            return "???"

    def noop(self, *args, **kwargs):  # TODO close popup window option
        return

    def finalize(self):  # ensure that there are no extra instances of the updater script
        super().finalize()
        if self.updater_pid > 0:
            qtile.cmd_spawn(f"kill -2 {self.updater_pid}")
