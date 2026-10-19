
package com.htmlhub.websiteapp;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

public class MainActivity extends Activity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());

        setContentView(webView);

        try {
            InputStream input =
                getAssets().open("start-url.txt");

            BufferedReader reader = new BufferedReader(
                new InputStreamReader(input, "UTF-8")
            );

            String url = reader.readLine();
            reader.close();

            if (url != null && url.startsWith("https://")) {
                webView.loadUrl(url);
            } else {
                loadLocalHtml();
            }

        } catch (Exception e) {
            loadLocalHtml();
        }
    }

    private void loadLocalHtml() {
        webView.loadUrl(
            "file:///android_asset/index.html"
        );
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
