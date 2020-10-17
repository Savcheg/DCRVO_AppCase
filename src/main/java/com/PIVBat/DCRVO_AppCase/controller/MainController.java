package com.PIVBat.DCRVO_AppCase.controller;

import com.PIVBat.DCRVO_AppCase.models.Post;
import com.PIVBat.DCRVO_AppCase.repo.PostRepostory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class MainController {
    @Autowired
    private PostRepostory postRep;
    @GetMapping("/")
    public String home(Model model) {
        Iterable<Post> posts = postRep.findAll();
        model.addAttribute("posts",posts);
        return "home";
    }

}