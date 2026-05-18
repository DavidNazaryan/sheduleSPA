# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keepclassmembers class * {
    @dagger.* <methods>;
}
-dontwarn dagger.internal.**
-keep class dagger.internal.** { *; }
