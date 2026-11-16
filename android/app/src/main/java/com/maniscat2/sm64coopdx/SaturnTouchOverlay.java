package com.maniscat2.sm64coopdx;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.util.SparseBooleanArray;
import android.view.MotionEvent;
import android.view.View;

import org.libsdl.app.SDLActivity;

/**
 * Optional transparent on-screen N64 controls.
 * Touches are forwarded through SDL's existing native touch entry point.
 */
final class SaturnTouchOverlay extends View {
    private static final int TOUCH_DEVICE_ID = 2901;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final SparseBooleanArray captured = new SparseBooleanArray();

    SaturnTouchOverlay(Context context) {
        super(context);
        setLayerType(View.LAYER_TYPE_HARDWARE, null);
        setClickable(true);
    }

    private float unit() { return Math.min(getWidth(), getHeight()); }

    private float joyX() { return getWidth() * 0.19f; }
    private float joyY() { return getHeight() * 0.78f; }
    private float joyRadius() { return unit() * 0.155f; }
    private float buttonRadius() { return unit() * 0.061f; }

    private float[] buttonCenter(int which) {
        switch (which) {
            case 0: return new float[]{getWidth() * 0.855f, getHeight() * 0.755f}; // A
            case 1: return new float[]{getWidth() * 0.705f, getHeight() * 0.855f}; // B
            case 2: return new float[]{getWidth() * 0.925f, getHeight() * 0.895f}; // Z
            default: return new float[]{getWidth() * 0.785f, getHeight() * 0.575f}; // Start
        }
    }

    private boolean isControl(float x, float y) {
        float dx = (x - joyX()) / joyRadius();
        float dy = (y - joyY()) / joyRadius();
        if (dx * dx + dy * dy <= 1.35f) return true;
        for (int i = 0; i < 4; i++) {
            float[] p = buttonCenter(i);
            float bx = x - p[0], by = y - p[1];
            if (bx * bx + by * by <= buttonRadius() * buttonRadius() * 2.2f) return true;
        }
        return false;
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (getWidth() == 0 || getHeight() == 0) return;

        float r = joyRadius();
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(0x55202020);
        canvas.drawCircle(joyX(), joyY(), r, paint);
        paint.setColor(0x88909090);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(unit() * 0.009f);
        canvas.drawCircle(joyX(), joyY(), r, paint);
        paint.setStyle(Paint.Style.FILL);
        canvas.drawCircle(joyX(), joyY(), r * 0.34f, paint);

        String[] labels = {"A", "B", "Z", "START"};
        for (int i = 0; i < 4; i++) {
            float[] p = buttonCenter(i);
            float br = buttonRadius();
            paint.setColor(i == 0 ? 0xAA2878D0 : (i == 1 ? 0xAADD5555 : 0xAA444444));
            canvas.drawCircle(p[0], p[1], br, paint);
            paint.setColor(0xDDFFFFFF);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(unit() * 0.006f);
            canvas.drawCircle(p[0], p[1], br, paint);
            paint.setStyle(Paint.Style.FILL);
            paint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setTextSize(i == 3 ? unit() * 0.026f : unit() * 0.045f);
            canvas.drawText(labels[i], p[0], p[1] + paint.getTextSize() * 0.35f, paint);
        }
    }

    private void send(MotionEvent event, int index, int action) {
        int id = event.getPointerId(index);
        float x = event.getX(index) / Math.max(1, getWidth());
        float y = event.getY(index) / Math.max(1, getHeight());
        float pressure = Math.max(0f, Math.min(1f, event.getPressure(index)));
        SDLActivity.onNativeTouch(TOUCH_DEVICE_ID, id, action, x, y, pressure);
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        int index = event.getActionIndex();
        boolean consumed = captured.size() > 0;

        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            if (isControl(event.getX(index), event.getY(index))) {
                int id = event.getPointerId(index);
                captured.put(id, true);
                send(event, index, action);
                invalidate();
                return true;
            }
            return consumed;
        }

        if (action == MotionEvent.ACTION_MOVE) {
            for (int i = 0; i < event.getPointerCount(); i++) {
                if (captured.get(event.getPointerId(i))) send(event, i, action);
            }
            return consumed;
        }

        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            int id = event.getPointerId(index);
            if (captured.get(id)) {
                send(event, index, action);
                captured.delete(id);
                invalidate();
                return true;
            }
            return consumed;
        }

        if (action == MotionEvent.ACTION_CANCEL) {
            for (int i = 0; i < event.getPointerCount(); i++) {
                if (captured.get(event.getPointerId(i))) {
                    send(event, i, MotionEvent.ACTION_UP);
                    captured.delete(event.getPointerId(i));
                }
            }
            invalidate();
            return consumed;
        }
        return consumed;
    }
}
