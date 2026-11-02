[app]
title = TikTok Browser
package.name = tiktokbrowser
package.domain = com.alpha.tiktok
source.dir = .
source.include_exts = py,kv,json,png,jpg
version = 1.0.0
requirements = python3,kivy==2.3.0,pyjnius,android
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
p4a.branch = develop
