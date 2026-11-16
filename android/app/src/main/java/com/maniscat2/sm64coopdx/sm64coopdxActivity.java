package com.maniscat2.sm64coopdx;

import android.content.res.AssetManager;
import android.os.Bundle;
import android.view.ViewGroup;

import org.libsdl.app.SDLActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class sm64coopdxActivity extends SDLActivity {
    @Override
    protected String[] getLibraries() {
        return new String[] { "SDL2", "main" };
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Copy packed resources before SDL starts the native game thread.
        try {
            copyGameAssetsOnce();
        } catch (IOException error) {
            throw new RuntimeException("Unable to prepare Saturn game resources", error);
        }

        super.onCreate(savedInstanceState);

        // Keep SDL's game surface underneath a transparent multi-touch overlay.
        if (mLayout != null) {
            SaturnTouchOverlay controls = new SaturnTouchOverlay(this);
            mLayout.addView(controls, new ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT));
            controls.bringToFront();
        }
    }

    private void copyGameAssetsOnce() throws IOException {
        File root = getFilesDir();
        File marker = new File(root, ".saturn-assets-ready");
        if (marker.isFile()) return;

        copyAssetTree("res", new File(root, "res"));
        copyAssetTree("fonts", new File(root, "fonts"));

        if (!marker.createNewFile()) {
            throw new IOException("Could not create resource-copy marker");
        }
    }

    private void copyAssetTree(String assetPath, File destination) throws IOException {
        AssetManager manager = getAssets();
        String[] children = manager.list(assetPath);
        if (children == null) throw new IOException("Missing packaged asset folder: " + assetPath);

        if (children.length > 0) {
            if (!destination.exists() && !destination.mkdirs()) {
                throw new IOException("Could not create " + destination);
            }
            for (String child : children) {
                copyAssetTree(assetPath + "/" + child, new File(destination, child));
            }
            return;
        }

        File parent = destination.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) {
            throw new IOException("Could not create " + parent);
        }
        try (InputStream input = manager.open(assetPath);
             OutputStream output = new FileOutputStream(destination)) {
            byte[] buffer = new byte[32768];
            int count;
            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
            }
        }
    }
}
