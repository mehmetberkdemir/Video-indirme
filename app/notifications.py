# -*- coding: utf-8 -*-
"""Windows toast bildirimleri – winotify sarmalayıcı."""


def notify(title: str, message: str, icon_type: str = "info"):
    """Windows toast bildirimi gönderir. Hata olursa sessizce geçer."""
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id="Video İndirici",
            title=title,
            msg=message,
            duration="short",
        )
        if icon_type == "error":
            toast.set_audio(audio.Default, loop=False)
        toast.show()
        return
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: win10toast
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
    except Exception:
        pass
