package com.maniscat2.sm64coopdx;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.CRC32;

public class RomSetupActivity extends Activity {
    private static final int REQUEST_ROM = 4102;
    private static final long ROM_BYTES = 8L * 1024L * 1024L;
    private static final long US_ROM_CRC32 = 0x3CE60709L;

    private TextView status;
    private Button chooseButton;
    private Button startButton;
    private File romFile;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        romFile = new File(getFilesDir(), "sm64.z64");

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        int pad = (int) (24 * getResources().getDisplayMetrics().density);
        layout.setPadding(pad, pad, pad, pad);

        TextView title = new TextView(this);
        title.setText("Saturn for Android");
        title.setTextSize(26);
        title.setTextColor(Color.BLACK);
        title.setGravity(Gravity.CENTER);
        layout.addView(title, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        status = new TextView(this);
        status.setTextColor(Color.DKGRAY);
        status.setTextSize(16);
        status.setGravity(Gravity.CENTER);
        status.setPadding(0, pad, 0, pad);
        layout.addView(status, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        chooseButton = new Button(this);
        chooseButton.setText("Choose US ROM");
        chooseButton.setOnClickListener(v -> openRomPicker());
        layout.addView(chooseButton);

        startButton = new Button(this);
        startButton.setText("Start Saturn");
        startButton.setOnClickListener(v -> launchGame());
        layout.addView(startButton);

        setContentView(layout);
        refreshState();
    }

    private void refreshState() {
        boolean valid = isValidUsRom(romFile);
        status.setText(valid
                ? "A valid US ROM is ready. Your ROM stays in this app's private storage."
                : "Select your own unmodified US Super Mario 64 ROM file (.z64). It will be checked and copied into private app storage.");
        startButton.setVisibility(valid ? View.VISIBLE : View.GONE);
    }

    private void openRomPicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(intent, REQUEST_ROM);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_ROM || resultCode != RESULT_OK || data == null || data.getData() == null) {
            return;
        }

        File temp = new File(getFilesDir(), "sm64.z64.pending");
        CRC32 crc = new CRC32();
        long total = 0;
        try (InputStream input = getContentResolver().openInputStream(data.getData());
             FileOutputStream output = new FileOutputStream(temp)) {
            if (input == null) throw new IOException("The selected file could not be opened.");
            byte[] buffer = new byte[32768];
            int count;
            while ((count = input.read(buffer)) != -1) {
                total += count;
                if (total > ROM_BYTES) throw new IOException("The selected file is larger than an N64 ROM.");
                crc.update(buffer, 0, count);
                output.write(buffer, 0, count);
            }
        } catch (IOException error) {
            temp.delete();
            status.setText("Could not read that file: " + error.getMessage());
            return;
        }

        if (total != ROM_BYTES || crc.getValue() != US_ROM_CRC32) {
            temp.delete();
            status.setText("That file is not the unmodified US ROM Saturn expects. Please select the correct .z64 file.");
            return;
        }

        if (romFile.exists() && !romFile.delete()) {
            temp.delete();
            status.setText("Could not replace the existing ROM file.");
            return;
        }
        if (!temp.renameTo(romFile)) {
            temp.delete();
            status.setText("Could not save the ROM in app storage.");
            return;
        }
        launchGame();
    }

    private boolean isValidUsRom(File file) {
        if (!file.isFile() || file.length() != ROM_BYTES) return false;
        CRC32 crc = new CRC32();
        try (InputStream input = new FileInputStream(file)) {
            byte[] buffer = new byte[32768];
            int count;
            while ((count = input.read(buffer)) != -1) crc.update(buffer, 0, count);
            return crc.getValue() == US_ROM_CRC32;
        } catch (IOException ignored) {
            return false;
        }
    }

    private void launchGame() {
        if (!isValidUsRom(romFile)) {
            refreshState();
            return;
        }
        startActivity(new Intent(this, sm64coopdxActivity.class));
        finish();
    }
}
