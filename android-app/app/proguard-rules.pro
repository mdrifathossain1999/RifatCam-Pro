# RifatCam Pro ProGuard Rules

# Keep CameraX
-keep class androidx.camera.** { *; }

# Keep ZXing
-keep class com.google.zxing.** { *; }

# Keep JSON
-keep class org.json.** { *; }

# Keep our app classes
-keep class com.rifatcam.pro.** { *; }

# Keep kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
