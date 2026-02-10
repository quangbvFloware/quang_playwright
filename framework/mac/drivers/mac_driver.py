# atomacos usage - Python 3 compatible fork of atomac. Requires macOS and accessibility permissions.
import atomacos


class MacDriver:
    def __init__(self, bundle_id: str):
        self.bundle_id = bundle_id
        self.app = atomacos.getAppRefByBundleId(bundle_id) or atomacos.launchAppByBundleId(bundle_id)


    def find(self, **kwargs):
        return self.app.findFirst(**kwargs)


    def quit(self):
        try:
            self.app.terminate()
        except Exception:
            pass