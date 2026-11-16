package com.maniscat2.sm64coopdx;

import android.os.Bundle;
import android.view.ViewGroup;

import org.libsdl.app.SDLActivity;

public class sm64coopdxActivity extends SDLActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
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
}
