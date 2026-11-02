[app]
title = TikTok Browser
package.name = tiktokbrowser
package.domain = com.alpha.tiktok
source.dir = .
source.include_exts = py,kv,json,png,jpg
version = 1.0.0
requirements = python3==3.11.9,kivy==2.3.1,pyjnius==1.6.1,android
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 24
android.ndk = 27c
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.accept_android_license = True
android.enable_androidx = True
android.gradle_dependencies = androidx.core:core:1.13.1
p4a.branch = master
