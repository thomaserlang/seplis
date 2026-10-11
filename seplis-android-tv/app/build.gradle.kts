plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.compose.compiler)
}

android {
    namespace = "net.seplis.tv"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "net.seplis.tv"
        minSdk = 30
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
        }
        create("fixture") {
            initWith(getByName("debug"))
            applicationIdSuffix = ".fixture"
            matchingFallbacks += "debug"
            buildConfigField("boolean", "USE_FIXTURES", "true")
        }
        release {
            optimization {
                enable = false
            }
        }
    }
    testBuildType = "fixture"
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    defaultConfig.buildConfigField("boolean", "USE_FIXTURES", "false")
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.foundation)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.icons)
    implementation(libs.androidx.tv.material)
    implementation(libs.coil.compose)
    implementation(libs.coil.network)
    implementation(libs.coroutines.android)
    implementation(libs.okhttp)
    implementation(libs.media3.exoplayer)
    implementation(libs.media3.hls)
    implementation(libs.media3.ui)
    implementation(libs.zxing.core)
    testImplementation(libs.junit)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    androidTestImplementation("androidx.test:runner:1.6.2")
    "fixtureImplementation"("androidx.compose.ui:ui-test-manifest")
}
