package net.seplis.tv.core.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import org.json.JSONArray
import org.json.JSONObject
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

data class Profile(val id: Int, val username: String, val token: String?)
data class ProfileSnapshot(
    val profiles: List<Profile> = emptyList(), val activeID: Int? = null, val pendingToken: String? = null,
)

interface ProfileStore {
    fun load(): ProfileSnapshot
    fun save(snapshot: ProfileSnapshot)
}

class AndroidProfileStore(context: Context) : ProfileStore {
    private val preferences = context.getSharedPreferences("secure_profiles", Context.MODE_PRIVATE)
    private val alias = "seplis_profiles"

    private fun key(): SecretKey {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(alias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").apply {
            init(KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build())
        }.generateKey()
    }

    override fun load(): ProfileSnapshot {
        val saved = preferences.getString("snapshot", null) ?: return ProfileSnapshot()
        val bytes = Base64.decode(saved, Base64.NO_WRAP)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, bytes.copyOfRange(0, 12)))
        val json = JSONObject(String(cipher.doFinal(bytes.copyOfRange(12, bytes.size)), Charsets.UTF_8))
        val records = json.optJSONArray("profiles") ?: JSONArray()
        return ProfileSnapshot(
            profiles = (0 until records.length()).map { records.getJSONObject(it) }.map {
                Profile(it.getInt("id"), it.getString("username"),
                    if (it.isNull("token")) null else it.getString("token"))
            },
            activeID = if (json.isNull("active_id")) null else json.getInt("active_id"),
            pendingToken = if (json.isNull("pending_token")) null else json.getString("pending_token"),
        )
    }

    override fun save(snapshot: ProfileSnapshot) {
        val json = JSONObject().apply {
            put("profiles", JSONArray().apply {
                snapshot.profiles.forEach { profile ->
                    put(JSONObject().put("id", profile.id).put("username", profile.username)
                        .put("token", profile.token ?: JSONObject.NULL))
                }
            })
            put("active_id", snapshot.activeID ?: JSONObject.NULL)
            put("pending_token", snapshot.pendingToken ?: JSONObject.NULL)
        }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val encrypted = cipher.iv + cipher.doFinal(json.toString().toByteArray(Charsets.UTF_8))
        check(preferences.edit().putString("snapshot", Base64.encodeToString(encrypted, Base64.NO_WRAP)).commit())
    }
}
