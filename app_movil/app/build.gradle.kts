plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "mx.microhubs.movil"
    compileSdk = 35
    defaultConfig {
        applicationId = "mx.microhubs.movil"; minSdk = 26; targetSdk = 35; versionCode = 1; versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
    buildTypes {
        getByName("debug") {
            val debugHost = providers.gradleProperty("debugHttpHost").getOrElse("10.0.2.2")
            require(debugHost.matches(Regex("[A-Za-z0-9.-]+")))
            buildConfigField("String", "HTTP_HOST", "\"$debugHost\"")
            resValue("string", "debug_http_host", debugHost)
        }
        getByName("release") { buildConfigField("String", "HTTP_HOST", "\"\"") }
    }
}
dependencies {
    implementation("com.journeyapps:zxing-android-embedded:4.3.0")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test:core:1.6.1")
}
